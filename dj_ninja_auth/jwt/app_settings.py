from typing import Union

from django.conf import settings
from django.utils.timezone import timedelta


class AppSettings(object):
    def __init__(self, prefix: str):
        self.prefix = prefix

        assert isinstance(self.VERIFY_SCHEMA, str)
        assert isinstance(self.PAIR_SCHEMA, str)
        assert isinstance(self.REFRESH_SCHEMA, str)
        assert isinstance(self.TOKEN_CLASSES, tuple)
        assert isinstance(self.USER_ID_CLAIM, str)
        assert isinstance(self.USER_ID_FIELD, str)
        assert isinstance(self.JTI_CLAIM, str)
        assert isinstance(self.TOKEN_TYPE_CLAIM, str)
        assert isinstance(self.USER_AUTHENTICATION_RULE, str)
        assert (isinstance(self.LEEWAY, (timedelta, int))) and not type(
            self.LEEWAY
        ) == bool
        assert isinstance(self.JWK_URL, (str, type(None)))
        assert isinstance(self.ISSUER, (str, type(None)))
        assert isinstance(self.AUDIENCE, (str, type(None)))
        assert isinstance(self.VERIFYING_KEY, (str, type(None)))
        assert isinstance(self.SIGNING_KEY, str)
        assert type(self.UPDATE_LAST_LOGIN) == bool
        assert isinstance(self.ALGORITHM, str)
        assert isinstance(self.ACCESS_TOKEN_LIFETIME, timedelta)
        assert isinstance(self.REFRESH_TOKEN_LIFETIME, timedelta)

        if self.ALGORITHM in ["RS256", "RS384", "RS512"]:
            assert isinstance(self.VERIFYING_KEY, str)

    def _setting(self, name, default):
        return getattr(settings, self.prefix + name, default)

    @property
    def VERIFY_SCHEMA(self) -> str:
        return self._setting(
            "VERIFY_SCHEMA", "dj_ninja_auth.jwt.schema.TokenVerifyInputSchema"
        )

    @property
    def PAIR_SCHEMA(self) -> str:
        return self._setting(
            "PAIR_SCHEMA", "dj_ninja_auth.jwt.schema.TokenPairInputSchema"
        )

    @property
    def REFRESH_SCHEMA(self) -> str:
        return self._setting(
            "REFRESH_SCHEMA", "dj_ninja_auth.jwt.schema.TokenRefreshInputSchema"
        )

    @property
    def TOKEN_CLASSES(self) -> tuple:
        return self._setting("TOKEN_CLASSES", ("dj_ninja_auth.jwt.tokens.AccessToken",))

    @property
    def USER_ID_CLAIM(self) -> str:
        return self._setting("USER_ID_CLAIM", "user_id")

    @property
    def USER_ID_FIELD(self) -> str:
        return self._setting("USER_ID_FIELD", "id")

    @property
    def JTI_CLAIM(self) -> str:
        return self._setting("JTI_CLAIM", "jti")

    @property
    def TOKEN_TYPE_CLAIM(self) -> str:
        return self._setting("TOKEN_TYPE_CLAIM", "token_type")

    @property
    def USER_AUTHENTICATION_RULE(self) -> str:
        return self._setting(
            "USER_AUTHENTICATION_RULE",
            "dj_ninja_auth.jwt.authentication.default_authentication_rule",
        )

    @property
    def LEEWAY(self) -> Union[int, timedelta]:
        return self._setting("LEEWAY", 0)

    @property
    def JWK_URL(self) -> Union[str, None]:
        return self._setting("JWK_URL", None)

    @property
    def ISSUER(self) -> Union[str, None]:
        return self._setting("ISSUER", None)

    @property
    def AUDIENCE(self) -> Union[str, None]:
        return self._setting("AUDIENCE", None)

    @property
    def VERIFYING_KEY(self) -> Union[str, None]:
        return self._setting("VERIFYING_KEY", None)

    @property
    def SIGNING_KEY(self) -> str:
        return self._setting("SIGNING_KEY", settings.SECRET_KEY)

    @property
    def ALGORITHM(self) -> str:
        return self._setting("ALGORITHM", "HS256")

    @property
    def UPDATE_LAST_LOGIN(self) -> bool:
        return self._setting("UPDATE_LAST_LOGIN", False)

    @property
    def ACCESS_TOKEN_LIFETIME(self) -> timedelta:
        return self._setting("ACCESS_TOKEN_LIFETIME", timedelta(minutes=5))

    @property
    def REFRESH_TOKEN_LIFETIME(self) -> timedelta:
        return self._setting("REFRESH_TOKEN_LIFETIME", timedelta(days=1))


_app_settings = AppSettings("AUTH_JWT_")


def __getattr__(name: str):
    return getattr(_app_settings, name)
