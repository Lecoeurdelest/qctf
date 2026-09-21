from flask import Blueprint, abort, request

from CTFd.constants.config import ConfigTypes
from CTFd.models import Files, Solutions, Teams, Users
from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.config.visibility import challenges_visible
from CTFd.utils.dates import ctf_ended, ctftime, view_after_ctf
from CTFd.utils.security.signing import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    unserialize,
)
from CTFd.utils.uploads import get_uploader

views = Blueprint("views", __name__)


@views.route("/files", defaults={"path": ""})
@views.route("/files/<path:path>")
def files(path):
    """
    Route in charge of dealing with making sure that CTF challenges are only accessible during the competition.
    :param path:
    :return:
    """
    f = Files.query.filter_by(location=path).first_or_404()
    if f.type == "challenge":
        if challenges_visible():
            if current_user.is_admin() is False:
                if not ctftime():
                    if ctf_ended() and view_after_ctf():
                        pass
                    else:
                        abort(403)
        else:
            # User cannot view challenges based on challenge visibility
            # e.g. ctf requires registration but user isn't authed or
            # ctf requires admin account but user isn't admin

            # Allow downloads if a valid token is provided
            # For example with wget downloads
            token = request.args.get("token", "")
            try:
                data = unserialize(token, max_age=3600)
            # The token isn't expired or broken
            except (BadTimeSignature, SignatureExpired, BadSignature):
                abort(403)

            # Determine the user and team asking to download
            user_id = data.get("user_id")
            team_id = data.get("team_id")
            file_id = data.get("file_id")
            user = Users.query.filter_by(id=user_id).first()
            team = Teams.query.filter_by(id=team_id).first()

            if not ctftime():
                # It's not CTF time. The only edge case is if the CTF is ended
                # but we have view_after_ctf enabled
                if ctf_ended() and view_after_ctf():
                    pass
                else:
                    if user.type == "admin":
                        # We allow admins to download files by URL before CTF start
                        pass
                    else:
                        # In all other situations we should block challenge files
                        abort(403)

            # Check user is admin if challenge_visibility is admins only
            if (
                get_config(ConfigTypes.CHALLENGE_VISIBILITY) == "admins"
                and user.type != "admin"
            ):
                abort(403)

            # Check that the user exists and isn't banned
            if user:
                if user.banned:
                    abort(403)
            else:
                abort(403)

            # Check that the team isn't banned
            if team:
                if team.banned:
                    abort(403)
            else:
                pass

            # Check that the token properly refers to the file
            if file_id != f.id:
                abort(403)

    elif f.type == "solution":
        s = Solutions.query.filter_by(id=f.solution_id).first_or_404()
        if s.state != "visible" or s.challenge.state != "visible":
            # Admins can see solution files for preview purposes
            if current_user.is_admin() is True:
                pass
            else:
                abort(404)

    uploader = get_uploader()
    try:
        return uploader.download(f.location)
    except IOError:
        abort(404)
