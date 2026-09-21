from flask import request

from CTFd.constants.email import (
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
)
from CTFd.utils import get_config
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email.providers.mailgun import MailgunEmailProvider
from CTFd.utils.email.providers.smtp import SMTPEmailProvider
from CTFd.utils.formatters import safe_format

PROVIDERS = {"smtp": SMTPEmailProvider, "mailgun": MailgunEmailProvider}


def sendmail(addr, text, subject="Message from {ctf_name}"):
    subject = safe_format(subject, ctf_name=get_config("ctf_name"))
    provider = get_mail_provider()
    EmailProvider = PROVIDERS.get(provider)
    if EmailProvider is None:
        return False, "No mail settings configured"
    return EmailProvider.sendmail(addr, text, subject)


def user_created_notification(addr, name, password):
    text = safe_format(
        get_config("user_creation_email_body") or DEFAULT_USER_CREATION_EMAIL_BODY,
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        url=request.url_root,
        name=name,
        password=password,
    )

    subject = safe_format(
        get_config("user_creation_email_subject")
        or DEFAULT_USER_CREATION_EMAIL_SUBJECT,
        ctf_name=get_config("ctf_name"),
    )
    return sendmail(addr=addr, text=text, subject=subject)


def check_email_is_whitelisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_whitelist = get_config("domain_whitelist")

    if domain_whitelist:
        domain_whitelist = [d.strip() for d in domain_whitelist.split(",")]

        for allowed_domain in domain_whitelist:
            if allowed_domain.startswith("*."):
                # domains should never container the "*" char
                if "*" in domain:
                    return False

                # Handle wildcard domain case
                suffix = allowed_domain[1:]  # Remove the "*" prefix
                if domain.endswith(suffix):
                    return True

            elif domain == allowed_domain:
                return True

        # whitelist is specified but the email doesn't match any domains
        return False

    # whitelist is not specified - allow all emails
    return True


def check_email_is_blacklisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_blacklist = get_config("domain_blacklist")

    if domain_blacklist:
        domain_blacklist = [d.strip() for d in domain_blacklist.split(",")]

        for disallowed_domain in domain_blacklist:
            if disallowed_domain.startswith("*."):
                # domains should never container the "*" char
                if "*" in domain:
                    return True

                # Handle wildcard domain case
                suffix = disallowed_domain[1:]  # Remove the "*" prefix
                if domain.endswith(suffix):
                    return True

            elif domain == disallowed_domain:
                return True

        # blacklist is specified but the email is not blacklisted
        return False

    # blacklist is not specified - no emails are blacklisted
    return False
