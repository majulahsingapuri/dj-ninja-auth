from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form
from ninja import ModelSchema, Schema
from ninja_extra import exceptions
from pydantic import EmailStr, SecretStr, model_validator

from ..schema import InputSchemaMixin
from ..schema_control import SchemaControl

allauth_enabled = "allauth" in settings.INSTALLED_APPS
if allauth_enabled:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.forms import SignupForm

UserModel = get_user_model()

schema = SchemaControl()

# Input/Output Schemas


class CreateUserSchema(InputSchemaMixin):
    username: str
    if allauth_enabled:
        if allauth_account_settings.EMAIL_REQUIRED:
            email: EmailStr
        else:
            email: Optional[EmailStr] = None
    password1: SecretStr
    password2: SecretStr
    _form: Optional[Form] = None

    def get_form(self):
        if allauth_enabled:
            return SignupForm
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
                email=getattr(self, "email", None),
            )
        )
        if not self._form.is_valid():
            raise exceptions.ValidationError(self._form.errors)
        return self

    def save(self, request):
        if allauth_enabled:
            try:
                return self._form.save(request)
            except ValueError:
                raise exceptions.ValidationError("Email already exists")
        else:
            return self._form.save()


class UpdateUserSchema(ModelSchema):
    class Meta:
        model = UserModel
        exclude = [
            "username",
            "email",
            "password",
            "id",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "groups",
            "user_permissions",
        ]
