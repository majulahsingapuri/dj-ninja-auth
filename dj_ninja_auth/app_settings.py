from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pydantic import HttpUrl, TypeAdapter, ValidationError


class AppSettings(object):
    def __init__(self, prefix: str):
        self.prefix = prefix
        assert isinstance(self.LOGIN_INPUT_SCHEMA, str)
        assert isinstance(self.SUCCESS_SCHEMA, str)
        assert isinstance(self.PASSWORD_CHANGE_SCHEMA, str)
        assert isinstance(self.PASSWORD_RESET_REQUEST_SCHEMA, str)
        assert isinstance(self.PASSWORD_RESET_CONFIRM_SCHEMA, str)
        assert isinstance(self.PASSWORD_RESET_URL, str)
        adapter = TypeAdapter(HttpUrl)
        try:
            adapter.validate_python(self.PASSWORD_RESET_URL)
        except ValidationError:
            raise ImproperlyConfigured("PASSWORD_RESET_URL is not a valid URL")

    def _setting(self, name, default):
        return getattr(settings, self.prefix + name, default)

    @property
    def LOGIN_INPUT_SCHEMA(self) -> str:
        return self._setting(
            "LOGIN_INPUT_SCHEMA", "dj_ninja_auth.schema.LoginInputSchema"
        )

    @property
    def SUCCESS_SCHEMA(self) -> str:
        return self._setting(
            "SUCCESS_SCHEMA", "dj_ninja_auth.schema.SuccessOutputSchema"
        )

    @property
    def PASSWORD_RESET_REQUEST_SCHEMA(self) -> str:
        return self._setting(
            "PASSWORD_RESET_REQUEST_SCHEMA",
            "dj_ninja_auth.schema.PasswordResetRequestInputSchema",
        )

    @property
    def PASSWORD_RESET_CONFIRM_SCHEMA(self) -> str:
        return self._setting(
            "PASSWORD_RESET_CONFIRM_SCHEMA",
            "dj_ninja_auth.schema.PasswordResetConfirmInputSchema",
        )

    @property
    def PASSWORD_CHANGE_SCHEMA(self) -> str:
        return self._setting(
            "PASSWORD_CHANGE_SCHEMA", "dj_ninja_auth.schema.PasswordChangeInputSchema"
        )

    @property
    def AUTH_USER_SCHEMA(self) -> str:
        return self._setting("AUTH_USER_SCHEMA", "dj_ninja_auth.schema.AuthUserSchema")

    @property
    def PASSWORD_RESET_URL(self) -> str:
        return self._setting("PASSWORD_RESET_URL", None)

    @property
    def API_NAMESPACE(self) -> str:
        return self._setting("API_NAMESPACE", "api-1.0.0")


_app_settings = AppSettings("AUTH_")


def __getattr__(name: str):
    return getattr(_app_settings, name)
