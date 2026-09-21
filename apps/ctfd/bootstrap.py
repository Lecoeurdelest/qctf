from CTFd import create_app
from CTFd.utils import get_config, set_config
from CTFd.utils.security.auth import generate_preset_admin


def bootstrap():
    app = create_app()
    with app.app_context(), app.test_request_context(environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        if generate_preset_admin() is None:
            raise RuntimeError("Preset email belongs to a non-admin; refusing to promote it")
        if get_config("setup"):
            return
        for key, value in {
            "ctf_name": "qctf",
            "user_mode": "teams",
            "challenge_visibility": "private",
            "scoreboard_visibility": "public",
            "account_visibility": "public",
            "registration_visibility": "private",
        }.items():
            set_config(key, value)
        set_config("setup", True)


if __name__ == "__main__":
    bootstrap()
