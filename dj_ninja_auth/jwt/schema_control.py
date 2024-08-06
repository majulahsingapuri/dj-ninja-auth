from typing import Type

from django.utils.module_loading import import_string

from ..schema import InputSchemaMixin
from . import app_settings
from .schema import JWTTokenInputSchemaMixin


class JWTSchemaControl:
    def __init__(self) -> None:

        self._verify_schema = import_string(app_settings.VERIFY_SCHEMA)
        self.validate_type(
            self._verify_schema, InputSchemaMixin, "AUTH_JWT_VERIFY_SCHEMA"
        )

        self._pair_schema = import_string(app_settings.PAIR_SCHEMA)
        self.validate_type(
            self._pair_schema,
            JWTTokenInputSchemaMixin,
            "AUTH_JWT_PAIR_SCHEMA",
        )

        self._refresh_schema = import_string(app_settings.REFRESH_SCHEMA)

        self.validate_type(
            self._refresh_schema,
            InputSchemaMixin,
            "AUTH_JWT_REFRESH_SCHEMA",
        )

    def validate_type(
        self, schema_type: Type, sub_class: Type, settings_key: str
    ) -> None:
        if not issubclass(schema_type, sub_class):
            raise Exception(f"{settings_key} type must inherit from `{sub_class}`")

    @property
    def verify_schema(self) -> "InputSchemaMixin":
        return self._verify_schema

    @property
    def pair_schema(self) -> "InputSchemaMixin":
        return self._pair_schema

    @property
    def refresh_schema(self) -> "InputSchemaMixin":
        return self._refresh_schema
