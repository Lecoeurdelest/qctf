from CTFd.constants import RawEnum


class ConfigTypes(str, RawEnum):
    CHALLENGE_VISIBILITY = "challenge_visibility"
    SCORE_VISIBILITY = "score_visibility"
    ACCOUNT_VISIBILITY = "account_visibility"
    REGISTRATION_VISIBILITY = "registration_visibility"


class UserModeTypes(str, RawEnum):
    USERS = "users"
    TEAMS = "teams"


class ChallengeVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    ADMINS = "admins"


class ScoreVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    HIDDEN = "hidden"
    ADMINS = "admins"


class AccountVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    ADMINS = "admins"


class RegistrationVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    MLC = "mlc"
