from django.conf import settings


class AppSettings(object):
    def __init__(self, prefix: str):
        self.prefix = prefix

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


_app_settings = AppSettings("NINJA_AUTH_REGISTRATION_")


def __getattr__(name: str):
    return getattr(_app_settings, name)
