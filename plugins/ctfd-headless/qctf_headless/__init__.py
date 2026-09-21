import json
import os
from http import HTTPStatus
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Blueprint, g, jsonify, request

from .auth import error, require_token


def load(app):
    api = Blueprint("qctf_headless", __name__, url_prefix="/api/qctf/v1")

    @api.get("/health")
    def health():
        return jsonify(success=True, data={"service": "ctfd", "status": "ok"})

    @api.get("/capabilities")
    def capabilities():
        return jsonify(success=True, data={
            "api_version": "v1",
            "headless": True,
            "auth": "ctfd-api-token",
            "instances": {"enabled": False, "reason": "Durable reconciler is not implemented"},
            "koth": {"enabled": False, "reason": "Claim verification and scoring ledger are not implemented"},
        })

    @api.get("/me")
    @require_token()
    def me():
        user = g.qctf_user
        return jsonify(success=True, data={
            "id": user.id, "name": user.name, "role": user.type,
            "team_id": user.team_id,
            "team_name": user.team.name if user.team else None,
        })

    @api.route("/challenges/<int:challenge_id>/instance", methods=["GET", "POST", "DELETE"])
    @require_token(team=True)
    def instance(challenge_id):
        return error("not_implemented", "Durable instance lifecycle is not implemented", 501)

    @api.get("/admin/runtime")
    @require_token(admin=True)
    def runtime():
        base = os.environ.get("ORCHESTRATOR_URL", "http://orchestrator:8081").rstrip("/")
        token = os.environ.get("ORCHESTRATOR_TOKEN", "")
        if not token:
            return error("runtime_unavailable", "Orchestrator credentials are missing", 503)
        upstream = Request(f"{base}/internal/v1/runtime", headers={"Authorization": f"Bearer {token}"})
        try:
            with urlopen(upstream, timeout=3) as response:
                data = json.load(response)
        except (URLError, TimeoutError, ValueError):
            return error("runtime_unavailable", "Orchestrator is unavailable", 503)
        return jsonify(success=True, data=data)

    def headless_only():
        if not request.path.startswith(("/api/", "/files/")):
            return error("ui_disabled", "CTFd UI is disabled; use the qctf web application", 404)

    def json_http_error(exception):
        status = getattr(exception, "code", 500)
        return error(f"http_{status}", HTTPStatus(status).phrase, status)

    @app.after_request
    def private_response(response):
        if request.path.startswith("/api/qctf/") or request.headers.get("Authorization"):
            response.headers["Cache-Control"] = "no-store"
        return response

    app.before_request_funcs.setdefault(None, []).insert(0, headless_only)
    for status in (400, 401, 403, 404, 405, 413, 429, 500, 502, 503):
        app.register_error_handler(status, json_http_error)
    app.register_blueprint(api)
