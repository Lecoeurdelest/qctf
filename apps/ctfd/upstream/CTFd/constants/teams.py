from collections import namedtuple

# TODO: CTFd 4.0. Consider changing to a dataclass
TeamAttrsFields = [
    "id",
    "oauth_id",
    "name",
    "email",
    "secret",
    "website",
    "affiliation",
    "country",
    "bracket_id",
    "hidden",
    "banned",
    "captain_id",
    "created",
]
TeamAttrs = namedtuple(
    "TeamAttrs",
    TeamAttrsFields,
    defaults=(None,) * len(TeamAttrsFields),
)
