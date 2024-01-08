from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form
from ninja import Schema
from ninja_extra import exceptions
from pydantic import SecretStr, model_validator

from ..schema import InputSchemaMixin
from ..schema_control import SchemaControl

UserModel = get_user_model()

schema = SchemaControl()

# Input/Output Schemas


class CreateUserSchema(InputSchemaMixin):
    username: str
    password1: SecretStr
    password2: SecretStr
    _form: Optional[Form] = None

    def get_form(self):
        return UserCreationForm

    @classmethod
    def get_response_schema(cls) -> type[Schema]:
        return schema.auth_user_schema

    @model_validator(mode="after")
    def check_user_form(self):
        self._form = self.get_form()(
            dict(
                username=self.username,
                password1=self.password1.get_secret_value(),
                password2=self.password2.get_secret_value(),
            )
        )
        if not self._form.is_valid():
            raise exceptions.ValidationError(self._form.errors)
        return self
