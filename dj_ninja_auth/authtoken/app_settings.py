from django.conf import settings
from django.utils.timezone import timedelta


class AppSettings(object):
    def __init__(self, prefix: str):
        self.prefix = prefix
        assert isinstance(self.MODEL, str)
        assert isinstance(self.EXPIRY, timedelta)
        assert isinstance(self.LOGIN_SCHEMA, str)

    def _setting(self, name, default):
        return getattr(settings, self.prefix + name, default)

    @property
    def MODEL(self) -> str:
        return self._setting("MODEL", "dj_ninja_auth.authtoken.models.Token")

    @property
    def EXPIRY(self) -> timedelta:
        return self._setting("EXPIRY", timedelta(days=1))

    @property
    def LOGIN_SCHEMA(self) -> str:
        return self._setting(
            "LOGIN_SCHEMA", "dj_ninja_auth.authtoken.schema.AuthTokenLoginInputSchema"
        )


_app_settings = AppSettings("NINJA_AUTH_TOKEN_")


def __getattr__(name: str):
    return getattr(_app_settings, name)
