from .. import allauth_enabled
from . import app_settings as registration_app_settings

if allauth_enabled:
    from allauth.account.adapter import DefaultAccountAdapter

    class NinjaAccountAdapter(DefaultAccountAdapter):
        def get_email_confirmation_url(self, request, emailconfirmation):
            return f"{registration_app_settings.EMAIL_CONFIRMATION_URL}?key={emailconfirmation.key}"
