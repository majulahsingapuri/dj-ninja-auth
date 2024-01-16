from typing import Type

from django.utils.module_loading import import_string

from ..schema import InputSchemaMixin
from . import app_settings as registration_app_settings
from .schema import UpdateUserSchema


class RegistrationSchemaControl:
    def __init__(self) -> None:
        self._create_user_schema = import_string(
            registration_app_settings.CREATE_USER_SCHEMA
        )
        self.validate_type(
            self._create_user_schema,
            InputSchemaMixin,
            "NINJA_AUTH_REGISTRATION_CREATE_USER_SCHEMA",
        )

        self._update_user_schema = import_string(
            registration_app_settings.UPDATE_USER_SCHEMA
        )
        self.validate_type(
            self._update_user_schema,
            UpdateUserSchema,
            "NINJA_AUTH_REGISTRATION_UPDATE_USER_SCHEMA",
        )

        self._verify_email_schema = import_string(
            registration_app_settings.VERIFY_EMAIL_SCHEMA
        )
        self.validate_type(
            self._verify_email_schema,
            InputSchemaMixin,
            "NINJA_AUTH_REGISTRATION_VERIFY_EMAIL_SCHEMA",
        )

        self._resend_email_schema = import_string(
            registration_app_settings.RESEND_EMAIL_SCHEMA
        )
        self.validate_type(
            self._resend_email_schema,
            InputSchemaMixin,
            "NINJA_AUTH_REGISTRATION_RESEND_EMAIL_SCHEMA",
        )

    def validate_type(
        self, schema_type: Type, sub_class: Type, settings_key: str
    ) -> None:
        if not issubclass(schema_type, sub_class):
            raise Exception(f"{settings_key} type must inherit from `{sub_class}`")

    @property
    def create_user_schema(self) -> "InputSchemaMixin":
        return self._create_user_schema

    @property
    def update_user_schema(self) -> "UpdateUserSchema":
        return self._update_user_schema

    @property
    def verify_email_schema(self) -> "InputSchemaMixin":
        return self._verify_email_schema

    @property
    def resend_email_schema(self) -> "InputSchemaMixin":
        return self._resend_email_schema
