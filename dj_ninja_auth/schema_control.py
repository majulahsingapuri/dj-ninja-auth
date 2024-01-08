from typing import Type

from django.utils.module_loading import import_string

from . import app_settings
from .schema import AuthUserSchema, InputSchemaMixin, SuccessMessageMixin


class SchemaControl:
    def __init__(self) -> None:
        self._login_schema = import_string(app_settings.LOGIN_INPUT_SCHEMA)
        self.validate_type(
            self._login_schema, InputSchemaMixin, "NINJA_AUTH_LOGIN_INPUT_SCHEMA"
        )

        self._success_schema = import_string(app_settings.SUCCESS_SCHEMA)
        self.validate_type(
            self._success_schema, SuccessMessageMixin, "NINJA_AUTH_SUCCESS_SCHEMA"
        )

        self._password_reset_request_schema = import_string(
            app_settings.PASSWORD_RESET_REQUEST_SCHEMA
        )
        self.validate_type(
            self._password_reset_request_schema,
            InputSchemaMixin,
            "NINJA_AUTH_PASSWORD_RESET_REQUEST_SCHEMA",
        )

        self._password_reset_confirm_schema = import_string(
            app_settings.PASSWORD_RESET_CONFIRM_SCHEMA
        )
        self.validate_type(
            self._password_reset_confirm_schema,
            InputSchemaMixin,
            "NINJA_AUTH_PASSWORD_RESET_CONFIRM_SCHEMA",
        )

        self._password_change_schema = import_string(
            app_settings.PASSWORD_CHANGE_SCHEMA
        )
        self.validate_type(
            self._password_change_schema,
            InputSchemaMixin,
            "NINJA_AUTH_PASSWORD_CHANGE_SCHEMA",
        )

        self._auth_user_schema = import_string(app_settings.AUTH_USER_SCHEMA)
        self.validate_type(
            self._auth_user_schema,
            AuthUserSchema,
            "NINJA_AUTH_AUTH_USER_SCHEMA",
        )

    def validate_type(
        self, schema_type: Type, sub_class: Type, settings_key: str
    ) -> None:
        if not issubclass(schema_type, sub_class):
            raise Exception(f"{settings_key} type must inherit from `{sub_class}`")

    @property
    def login_schema(self) -> "InputSchemaMixin":
        return self._login_schema

    @property
    def success_schema(self) -> "SuccessMessageMixin":
        return self._success_schema

    @property
    def password_reset_request_schema(self) -> "InputSchemaMixin":
        return self._password_reset_request_schema

    @property
    def password_reset_confirm_schema(self) -> "InputSchemaMixin":
        return self._password_reset_confirm_schema

    @property
    def password_change_schema(self) -> "InputSchemaMixin":
        return self._password_change_schema

    @property
    def auth_user_schema(self) -> "AuthUserSchema":
        return self._auth_user_schema
