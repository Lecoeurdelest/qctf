from markupsafe import Markup


def markup(text):
    return Markup(text)  # nosec B704
