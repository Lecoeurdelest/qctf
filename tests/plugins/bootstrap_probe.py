import os
import sys

sys.path.insert(0, "/opt/qctf")

from bootstrap import bootstrap
from CTFd import create_app
from CTFd.models import Users
from CTFd.utils import get_config
from CTFd.utils.config import get_themes

if not os.environ["DATABASE_URL"].startswith("sqlite:////tmp/"):
    raise RuntimeError("This probe is restricted to a disposable SQLite database")

bootstrap()
bootstrap()
app = create_app()
with app.app_context():
    assert get_themes() == [], "Headless runtime must not bundle UI themes"
    assert not os.path.isdir(os.path.join(app.root_path, "themes", "admin"))
    assert Users.query.count() == 1, "Bootstrap must be idempotent"
    assert Users.query.one().type == "admin"
    assert get_config("setup") == 1
    assert get_config("user_mode") == "teams"
with app.test_client() as client:
    response = client.get("/admin")
    assert response.status_code == 404
    assert response.json["errors"]["code"] == "ui_disabled"
    response = client.get("/api/qctf/v1/me", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ['PRESET_ADMIN_TOKEN']}",
    })
    assert response.status_code == 200
    assert response.json["data"]["role"] == "admin"
print("PASS fresh database bootstrap, repeated bootstrap, headless guard and preset token")
