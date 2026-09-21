import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask, abort

from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.plugins.qctf_headless import load as load_headless
from CTFd.plugins.qctf_koth import load as load_koth


class PluginContractTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        load_headless(self.app)
        load_koth(self.app)
        self.app.add_url_rule("/api/upstream-auth-failure", view_func=lambda: abort(401))
        self.client = self.app.test_client()
        self.user = SimpleNamespace(
            id=7, name="player", type="user", banned=False, team_id=42,
            team=SimpleNamespace(name="team-42", banned=False),
        )
        self.lookup = patch("CTFd.plugins.qctf_headless.auth.lookup_user_token", return_value=self.user)
        self.mock_lookup = self.lookup.start()
        self.addCleanup(self.lookup.stop)
        self.headers = {"Authorization": "Token test-token", "Content-Type": "application/json"}

    def test_no_ctfd_ui_routes(self):
        for path in ["/", "/login", "/admin", "/admin/challenges", "/setup", "/themes/core/static/x.js"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json["errors"]["code"], "ui_disabled")

    def test_upstream_auth_errors_are_json(self):
        response = self.client.get("/api/upstream-auth-failure")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["errors"]["code"], "http_401")

    def test_missing_token_and_wrong_scheme_rejected(self):
        for auth in ["", "Bearer test-token", "Token ", "Token  test-token"]:
            with self.subTest(auth=auth):
                response = self.client.get("/api/qctf/v1/me", headers={"Authorization": auth})
                self.assertEqual(response.status_code, 401)
        self.mock_lookup.assert_not_called()

    def test_invalid_and_expired_tokens_rejected(self):
        for exception in [UserNotFoundException, UserTokenExpiredException]:
            self.mock_lookup.side_effect = exception
            response = self.client.get("/api/qctf/v1/me", headers=self.headers)
            self.assertEqual(response.status_code, 401)

    def test_team_id_comes_from_principal_not_request(self):
        response = self.client.get("/api/qctf/v1/me?team_id=999", headers={**self.headers, "X-Team-Id": "999"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["team_id"], 42)
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_banned_user_or_team_rejected(self):
        self.user.banned = True
        self.assertEqual(self.client.get("/api/qctf/v1/me", headers=self.headers).status_code, 403)
        self.user.banned = False
        self.user.team.banned = True
        self.assertEqual(self.client.get("/api/qctf/v1/me", headers=self.headers).status_code, 403)

    def test_control_center_requires_admin(self):
        response = self.client.get("/api/qctf/v1/admin/runtime", headers=self.headers)
        self.assertEqual(response.status_code, 403)

    def test_admin_without_service_secret_fails_closed(self):
        self.user.type = "admin"
        with patch.dict("os.environ", {"ORCHESTRATOR_TOKEN": ""}):
            response = self.client.get("/api/qctf/v1/admin/runtime", headers=self.headers)
        self.assertEqual(response.status_code, 503)

    def test_team_required_even_if_client_supplies_team_id(self):
        self.user.team_id = None
        self.user.team = None
        for path in ["/api/qctf/v1/challenges/1/instance", "/api/qctf/v1/koth/arenas/1/claims"]:
            with self.subTest(path=path):
                response = self.client.post(path, headers=self.headers, json={"team_id": 999})
                self.assertEqual(response.status_code, 403)

    def test_unimplemented_lifecycle_and_claims_do_not_report_success(self):
        for path in ["/api/qctf/v1/challenges/1/instance", "/api/qctf/v1/koth/arenas/1/claims"]:
            with self.subTest(path=path):
                response = self.client.post(path, headers=self.headers, json={})
                self.assertEqual(response.status_code, 501)
                self.assertFalse(response.json["success"])

    def test_capabilities_are_honest(self):
        data = self.client.get("/api/qctf/v1/capabilities").json["data"]
        self.assertTrue(data["headless"])
        self.assertFalse(data["instances"]["enabled"])
        self.assertFalse(data["koth"]["enabled"])
        self.assertFalse(self.client.get("/api/qctf/v1/koth/capabilities").json["data"]["scoring"])


if __name__ == "__main__":
    unittest.main()
