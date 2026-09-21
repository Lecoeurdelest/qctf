from functools import wraps

from flask import g, jsonify, request

from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.utils.security.auth import lookup_user_token


def error(code, message, status):
    return jsonify(success=False, errors={"code": code, "message": message}), status


def require_token(*, admin=False, team=False):
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            scheme, _, token = request.headers.get("Authorization", "").partition(" ")
            if scheme != "Token" or not token or token.strip() != token:
                return error("authentication_required", "A CTFd API token is required", 401)
            try:
                user = lookup_user_token(token)
            except (UserNotFoundException, UserTokenExpiredException):
                return error("invalid_token", "The API token is invalid or expired", 401)
            if user.banned or (user.team and user.team.banned):
                return error("account_disabled", "This account or team is disabled", 403)
            if admin and user.type != "admin":
                return error("admin_required", "An administrator is required", 403)
            if team and user.team_id is None:
                return error("team_required", "Join a team before requesting an instance", 403)
            g.qctf_user = user
            return view(*args, **kwargs)

        return wrapped

    return decorate

