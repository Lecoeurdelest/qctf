import sys
import time
from distutils.version import StrictVersion

from flask import Flask, Request
from flask_babel import Babel
from flask_migrate import upgrade
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.wsgi import get_host

from CTFd import utils
from CTFd.plugins import init_plugins
from CTFd.utils.initialization import (
    init_cli,
    init_events,
    init_logs,
    init_request_processors,
)
from CTFd.utils.migrations import create_database, migrations, stamp_latest_revision
from CTFd.utils.sessions import CachingSessionInterface
from CTFd.utils.updates import update_check
from CTFd.utils.user import get_locale

__version__ = "3.8.7"
__channel__ = "oss"


class CTFdRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Hijack the original Flask request path because it does not account for subdirectory deployments in an intuitive
        manner. We append script_root so that the path always points to the full path as seen in the browser.
        e.g. /subdirectory/path/route vs /path/route
        """
        self.path = self.script_root + self.path


class CTFdFlask(Flask):
    def __init__(self, *args, **kwargs):
        self.session_interface = CachingSessionInterface(key_prefix="session")
        self.request_class = CTFdRequest

        Flask.__init__(self, *args, **kwargs)

    def create_url_adapter(self, request):
        # TODO: Backport of TRUSTED_HOSTS behavior from Flask. Remove when possible.
        # https://github.com/pallets/flask/pull/5637
        if request is not None:
            if (trusted_hosts := self.config.get("TRUSTED_HOSTS")) is not None:
                request.trusted_hosts = trusted_hosts

            # Check trusted_hosts here until bind_to_environ does.
            request.host = get_host(request.environ, request.trusted_hosts)
        return super(CTFdFlask, self).create_url_adapter(request)


def confirm_upgrade():
    if sys.stdin.isatty():
        print("/*\\ CTFd has updated and must update the database! /*\\")
        print("/*\\ Please backup your database before proceeding! /*\\")
        print("/*\\ CTFd maintainers are not responsible for any data loss! /*\\")
        if input("Run database migrations (Y/N)").lower().strip() == "y":  # nosec B322
            return True
        else:
            print("/*\\ Ignored database migrations... /*\\")
            return False
    else:
        return True


def run_upgrade():
    upgrade()
    utils.set_config("ctf_version", __version__)


def create_app(config="CTFd.config.Config"):
    app = CTFdFlask(__name__, static_folder=None, template_folder=None)
    with app.app_context():
        app.config.from_object(config)

        from CTFd.cache import cache
        from CTFd.utils import import_in_progress

        cache.init_app(app)
        app.cache = cache

        # If we are importing we should pause startup until the import is finished
        while import_in_progress():
            print("Import currently in progress, CTFd startup paused for 5 seconds")
            time.sleep(5)

        from CTFd.models import (  # noqa: F401
            Challenges,
            Fails,
            Files,
            Flags,
            Solves,
            Tags,
            Teams,
            Tracking,
            db,
        )

        url = create_database()

        # This allows any changes to the SQLALCHEMY_DATABASE_URI to get pushed back in
        # This is mostly so we can force MySQL's charset
        app.config["SQLALCHEMY_DATABASE_URI"] = str(url)

        # Register database
        db.init_app(app)

        # Register Flask-Migrate
        migrations.init_app(app, db)

        babel = Babel()
        babel.locale_selector_func = get_locale
        babel.init_app(app)

        # Alembic sqlite support is lacking so we should just create_all anyway
        if url.drivername.startswith("sqlite"):
            # Enable foreign keys for SQLite. This must be before the
            # db.create_all call because tests use the in-memory SQLite
            # database (each connection, including db creation, is a new db).
            # https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#foreign-key-support
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            db.create_all()
            stamp_latest_revision()
        else:
            # This creates tables instead of db.create_all()
            # Allows migrations to happen properly
            upgrade()

        from CTFd.models import ma

        ma.init_app(app)

        app.db = db
        app.VERSION = __version__
        app.CHANNEL = __channel__

        reverse_proxy = app.config.get("REVERSE_PROXY")
        if reverse_proxy:
            if type(reverse_proxy) is str and "," in reverse_proxy:
                proxyfix_args = [int(i) for i in reverse_proxy.split(",")]
                app.wsgi_app = ProxyFix(app.wsgi_app, *proxyfix_args)
            else:
                # TODO: CTFd 4.0 We should deprecate this behavior and require that users specify the level of control they want
                # Maybe investigate Django to see what they do
                app.wsgi_app = ProxyFix(
                    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=0
                )

        version = utils.get_config("ctf_version")

        # Upgrading from an older version of CTFd
        if version and (StrictVersion(version) < StrictVersion(__version__)):
            if confirm_upgrade():
                run_upgrade()
            else:
                exit()

        if not version:
            utils.set_config("ctf_version", __version__)

        update_check(force=True)

        init_request_processors(app)
        from CTFd.api import api
        from CTFd.views import views

        app.register_blueprint(api)
        app.register_blueprint(views)

        init_logs(app)
        init_events(app)
        init_plugins(app)
        init_cli(app)

        return app
