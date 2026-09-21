import datetime
import logging
import os
import sys

from flask import abort, request, session
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from CTFd.cache import clear_user_recent_ips
from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import Tracking, db
from CTFd.utils import get_app_config, import_in_progress
from CTFd.utils.config import is_setup
from CTFd.utils.events import EventManager, RedisEventManager
from CTFd.utils.security.auth import login_user, logout_user, lookup_user_token
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.user import (
    authed,
    get_current_team_attrs,
    get_current_user_attrs,
    get_current_user_recent_ips,
    get_ip,
)


def init_cli(app):
    from CTFd.cli import _cli

    app.register_blueprint(_cli, cli_group=None)


def init_logs(app):
    logger_submissions = logging.getLogger("submissions")
    logger_logins = logging.getLogger("logins")
    logger_registrations = logging.getLogger("registrations")

    logger_submissions.setLevel(logging.INFO)
    logger_logins.setLevel(logging.INFO)
    logger_registrations.setLevel(logging.INFO)

    log_dir = app.config["LOG_FOLDER"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = {
        "submissions": os.path.join(log_dir, "submissions.log"),
        "logins": os.path.join(log_dir, "logins.log"),
        "registrations": os.path.join(log_dir, "registrations.log"),
    }

    try:
        for log in logs.values():
            if not os.path.exists(log):
                open(log, "a").close()

        submission_log = logging.handlers.RotatingFileHandler(
            logs["submissions"], maxBytes=10485760, backupCount=5
        )
        login_log = logging.handlers.RotatingFileHandler(
            logs["logins"], maxBytes=10485760, backupCount=5
        )
        registration_log = logging.handlers.RotatingFileHandler(
            logs["registrations"], maxBytes=10485760, backupCount=5
        )

        logger_submissions.addHandler(submission_log)
        logger_logins.addHandler(login_log)
        logger_registrations.addHandler(registration_log)
    except IOError:
        pass

    stdout = logging.StreamHandler(stream=sys.stdout)

    logger_submissions.addHandler(stdout)
    logger_logins.addHandler(stdout)
    logger_registrations.addHandler(stdout)

    logger_submissions.propagate = 0
    logger_logins.propagate = 0
    logger_registrations.propagate = 0


def init_events(app):
    if app.config.get("CACHE_TYPE") == "redis":
        app.events_manager = RedisEventManager()
    elif app.config.get("CACHE_TYPE") == "filesystem":
        app.events_manager = EventManager()
    else:
        app.events_manager = EventManager()
    app.events_manager.listen()


def init_request_processors(app):
    application_root = app.config.get("APPLICATION_ROOT", "/")

    @app.before_request
    def needs_setup():
        if import_in_progress():
            abort(503, description="Import currently in progress")
        if not is_setup() and request.endpoint != "qctf_headless.health":
            abort(503, description="Run the qctf bootstrap before serving API requests")

    @app.before_request
    def tokens():
        token = request.headers.get("Authorization")
        if token:
            try:
                token_type, token = token.split(" ", 1)
                if token_type != "Token" or not token or token.strip() != token:
                    abort(401)
                user = lookup_user_token(token)
            except UserNotFoundException:
                abort(401, description="Your access token is invalid")
            except UserTokenExpiredException:
                abort(401, description="Your access token has expired")
            except Exception:
                abort(401, description="Invalid authorization header")
            else:
                login_user(user)

    @app.before_request
    def account_status():
        if authed():
            user = get_current_user_attrs()
            team = get_current_team_attrs()
            if (user and user.banned) or (team and team.banned):
                abort(403, description="This account or team is disabled")
            if user and user.change_password:
                abort(403, description="A password change is required")

    @app.before_request
    def tracker():
        if authed():
            user_ips = get_current_user_recent_ips()
            ip = get_ip()

            track = None
            if ip not in user_ips or request.method in (
                "POST",
                "PATCH",
                "PUT",
                "DELETE",
            ):
                track = Tracking.query.filter_by(
                    ip=get_ip(), user_id=session["id"]
                ).first()

                if track:
                    track.date = datetime.datetime.utcnow()
                else:
                    track = Tracking(ip=get_ip(), user_id=session["id"])
                    db.session.add(track)

            if track:
                try:
                    db.session.commit()
                except (InvalidRequestError, IntegrityError):
                    db.session.rollback()
                    db.session.close()
                    logout_user()
                else:
                    clear_user_recent_ips(user_id=session["id"])

    @app.before_request
    def csrf():
        # TODO: CTFd 4.0 Consider reorganizing this function to only run on non safe methods
        # Early exit: no CSRF for functions explicitly marked as bypassing CSRF
        try:
            func = app.view_functions[request.endpoint]
        except KeyError:
            abort(404)
        if hasattr(func, "_bypass_csrf"):
            return
        safe_methods = ("GET", "HEAD", "OPTIONS", "TRACE")
        # Tokens are validated before this processor runs.
        if request.headers.get("Authorization"):
            return
        # Ensure a session and CSRF nonce are present
        if not session.get("nonce"):
            session["nonce"] = generate_nonce()
        if request.method not in safe_methods:
            if request.is_json:
                # API requests with JSON body => token in header
                if session["nonce"] != request.headers.get("CSRF-Token"):
                    abort(403)
            else:
                abort(403)

    @app.after_request
    def response_headers(response):
        response.headers["Cross-Origin-Opener-Policy"] = get_app_config(
            "CROSS_ORIGIN_OPENER_POLICY", default="same-origin-allow-popups"
        )
        return response

    if application_root != "/":
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {application_root: app})
