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


_app_settings = AppSettings("NINJA_AUTH_REGISTRATION_")


def __getattr__(name: str):
    return getattr(_app_settings, name)
