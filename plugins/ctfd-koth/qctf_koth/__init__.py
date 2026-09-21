from flask import Blueprint, jsonify

from CTFd.plugins.qctf_headless.auth import error, require_token


def load(app):
    api = Blueprint("qctf_koth", __name__, url_prefix="/api/qctf/v1/koth")

    @api.get("/capabilities")
    def capabilities():
        return jsonify(success=True, data={
            "mode": "shared-arena",
            "enabled": False,
            "claims": False,
            "scoring": False,
            "reason": "Requires proof verifier, transactional ownership and an idempotent Award ledger",
        })

    @api.get("/arenas")
    @require_token()
    def arenas():
        return error("not_implemented", "KoTH arena storage is not implemented", 501)

    @api.post("/arenas/<int:arena_id>/claims")
    @require_token(team=True)
    def claim(arena_id):
        return error("not_implemented", "KoTH proof verification and ownership are not implemented", 501)

    app.register_blueprint(api)

