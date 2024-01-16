from django.conf import settings

from .. import app_settings

allauth_enabled = "allauth" in settings.INSTALLED_APPS
if allauth_enabled:
    from allauth.account.adapter import DefaultAccountAdapter

    class NinjaAccountAdapter(DefaultAccountAdapter):
        def get_email_confirmation_url(self, request, emailconfirmation):
            return f"{app_settings.EMAIL_CONFIRMATION_URL}?key={emailconfirmation.key}"
