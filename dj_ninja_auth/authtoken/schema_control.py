from typing import Type

from django.utils.module_loading import import_string

from ..schema import InputSchemaMixin
from . import app_settings


class AuthTokenSchemaControl:
    def __init__(self) -> None:

        self._token_login_schema = import_string(app_settings.LOGIN_SCHEMA)
        self.validate_type(
            self._token_login_schema, InputSchemaMixin, "AUTH_TOKEN_LOGIN_SCHEMA"
        )

    def validate_type(
        self, schema_type: Type, sub_class: Type, settings_key: str
    ) -> None:
        if not issubclass(schema_type, sub_class):
            raise Exception(f"{settings_key} type must inherit from `{sub_class}`")

    @property
    def token_login_schema(self) -> "InputSchemaMixin":
        return self._token_login_schema
