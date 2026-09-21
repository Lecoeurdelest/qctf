"""Integration checks run only by bootstrap_probe on its disposable database."""
import io
import os
from pathlib import Path


def check_headless_backend(app):
    from CTFd.models import Teams, Users, db
    from CTFd.utils import set_config
    from CTFd.utils.security.auth import generate_user_token

    with app.app_context():
        team = Teams(name="headless-probe-team")
        db.session.add(team)
        db.session.flush()
        user = Users(
            name="headless-probe",
            email="probe@example.test",
            password="test-password",
            team_id=team.id,
        )
        db.session.add(user)
        db.session.flush()
        token = generate_user_token(user)
        player_token = token.value
        user_id, team_id = user.id, team.id
        set_config("score_visibility", "public")

    headers = {"Authorization": f"Token {os.environ['PRESET_ADMIN_TOKEN']}"}
    player_headers = {"Authorization": f"Token {player_token}"}
    client = app.test_client(use_cookies=False)

    def call(method, path, status=200, **kwargs):
        response = getattr(client, method)(path, **kwargs)
        assert response.status_code == status, (
            method,
            path,
            response.status_code,
            response.get_data(as_text=True)[:500],
        )
        assert response.is_json, (path, response.content_type)
        assert "Location" not in response.headers, path
        return response.json

    def no_ui(data):
        if isinstance(data, dict):
            assert not {
                "template",
                "templates",
                "script",
                "scripts",
                "view",
                "create",
            }.intersection(data), data
            for value in data.values():
                no_ui(value)
        elif isinstance(data, list):
            for value in data:
                no_ui(value)

    routes = list(app.url_map.iter_rules())
    assert all(rule.rule.startswith(("/api/", "/files")) for rule in routes), routes
    assert not app.static_folder and not app.template_folder
    assert not any(Path(app.root_path).rglob("*.html"))
    assert not any(Path(app.root_path).rglob("*.js"))
    for path in [
        "/",
        "/login",
        "/register",
        "/reset_password",
        "/setup",
        "/admin",
        "/admin/challenges",
        "/challenges",
        "/scoreboard",
        "/themes/core/static/x.js",
        "/plugins/challenges/assets/view.html",
        "/plugins/flags/assets/static/create.html",
    ]:
        call("get", path, 404)
    for path in [
        "/api/v1/challenges",
        "/api/v1/challenges/types",
        "/api/v1/flags/types",
        "/api/v1/users/me",
    ]:
        call("get", path, 403)
    call("get", "/api/v1/users/me", 401, headers={"Authorization": "Bearer invalid"})
    call("get", "/api/v1/challenges/types", 403, headers=player_headers)
    for path in [
        "/api/v1/challenges/types",
        "/api/v1/flags/types",
        "/api/v1/flags/types/static",
        "/api/v1/flags/types/regex",
    ]:
        no_ui(call("get", path, headers=headers)["data"])

    for kind in ["standard", "dynamic"]:
        payload = {
            "name": f"Probe {kind}",
            "category": "test",
            "description": "Headless API challenge",
            "value": 100,
            "type": kind,
            "state": "visible",
        }
        if kind == "dynamic":
            payload.update(initial=100, minimum=10, decay=10, function="linear")
        challenge = call("post", "/api/v1/challenges", headers=headers, json=payload)[
            "data"
        ]
        cid = challenge["id"]
        no_ui(challenge)
        for flag_type, content in [
            ("static", "flag{headless}"),
            ("regex", "flag\\{regex\\}"),
        ]:
            flag = call(
                "post",
                "/api/v1/flags",
                headers=headers,
                json={
                    "challenge_id": cid,
                    "type": flag_type,
                    "content": content,
                    "data": "",
                },
            )["data"]
            no_ui(call("get", f"/api/v1/flags/{flag['id']}", headers=headers)["data"])
        no_ui(call("get", "/api/v1/challenges", headers=player_headers)["data"])
        no_ui(call("get", f"/api/v1/challenges/{cid}", headers=player_headers)["data"])
        call(
            "patch",
            f"/api/v1/challenges/{cid}",
            headers=headers,
            json={"description": "Updated through API"},
        )
        call(
            "post",
            "/api/v1/files",
            headers=headers,
            data={
                "challenge_id": str(cid),
                "type": "challenge",
                "file": (io.BytesIO(b"headless attachment"), "probe.txt"),
            },
        )
        detail = call("get", f"/api/v1/challenges/{cid}", headers=player_headers)[
            "data"
        ]
        assert detail["files"]
        download = client.get(detail["files"][0], headers=player_headers)
        assert download.status_code == 200 and download.data == b"headless attachment"
        result = call(
            "post",
            "/api/v1/challenges/attempt",
            headers=player_headers,
            json={"challenge_id": cid, "submission": "flag{headless}"},
        )
        assert result["data"]["status"] == "correct", result
        no_ui(
            call("get", f"/api/v1/challenges/{cid}/solves", headers=player_headers)[
                "data"
            ]
        )

    scores = call("get", "/api/v1/scoreboard")["data"]
    assert any(entry["account_id"] == team_id for entry in scores), scores
    for entry in scores:
        call("get", entry["account_url"], headers=headers)
    call("get", "/api/v1/statistics/progression/matrix", headers=headers)
    call("get", f"/api/v1/users/{user_id}", headers=headers)
    call("get", f"/api/v1/teams/{team_id}", headers=headers)

    with app.app_context():
        Users.query.get(user_id).banned = True
        db.session.commit()
        app.cache.clear()
    call("get", "/api/v1/challenges", 403, headers=player_headers)
    with app.app_context():
        Users.query.get(user_id).banned = False
        Users.query.get(user_id).change_password = True
        db.session.commit()
        app.cache.clear()
    call("get", "/api/v1/challenges", 403, headers=player_headers)
    with app.app_context():
        set_config("setup", False)
    call("get", "/api/v1/challenges", 503)
    call("get", "/api/qctf/v1/health")
    print(
        "PASS headless route map, asset removal, JSON denials, challenge/flag APIs, uploads, solves, scoreboard and statistics"
    )
