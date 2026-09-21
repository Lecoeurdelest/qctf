from collections import namedtuple

# TODO: CTFd 4.0. Consider changing to a dataclass
UserAttrsFields = [
    "id",
    "oauth_id",
    "name",
    "email",
    "type",
    "secret",
    "website",
    "affiliation",
    "country",
    "bracket_id",
    "hidden",
    "banned",
    "verified",
    "language",
    "team_id",
    "created",
    "change_password",
]
UserAttrs = namedtuple(
    "UserAttrs", UserAttrsFields, defaults=(None,) * len(UserAttrsFields)
)
