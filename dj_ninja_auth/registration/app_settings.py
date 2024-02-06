from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pydantic import HttpUrl, TypeAdapter, ValidationError


class AppSettings(object):
    def __init__(self, prefix: str):
        self.prefix = prefix
        adapter = TypeAdapter(HttpUrl)
        assert isinstance(self.EMAIL_CONFIRMATION_URL, str)
        try:
            adapter.validate_python(self.EMAIL_CONFIRMATION_URL)
        except ValidationError:
            raise ImproperlyConfigured("EMAIL_CONFIRMATION_URL is not a valid URL")

    def _setting(self, name, default):
        return getattr(settings, self.prefix + name, default)

    @property
    def CREATE_USER_SCHEMA(self) -> str:
        return self._setting(
            "CREATE_USER_SCHEMA", "dj_ninja_auth.registration.schema.CreateUserSchema"
        )

    @property
    def UPDATE_USER_SCHEMA(self) -> str:
        return self._setting(
            "UPDATE_USER_SCHEMA", "dj_ninja_auth.registration.schema.UpdateUserSchema"
        )

    @property
    def VERIFY_EMAIL_SCHEMA(self) -> str:
        return self._setting(
            "VERIFY_EMAIL_SCHEMA", "dj_ninja_auth.registration.schema.VerifyEmailSchema"
        )

    @property
    def RESEND_EMAIL_SCHEMA(self) -> str:
        return self._setting(
            "RESEND_EMAIL_SCHEMA", "dj_ninja_auth.registration.schema.ResendEmailSchema"
        )

    @property
    def EMAIL_CONFIRMATION_URL(self) -> str:
        return self._setting("EMAIL_CONFIRMATION_URL", None)


_app_settings = AppSettings("REGISTRATION_")


def __getattr__(name: str):
    return getattr(_app_settings, name)
