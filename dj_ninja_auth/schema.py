from typing import Optional, Type

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode as uid_decoder
from ninja import ModelSchema, Schema
from ninja_extra import exceptions
from pydantic import EmailStr, SecretStr, model_validator

UserModel = get_user_model()

# Mixins


class InputSchemaMixin(Schema):
    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        raise NotImplementedError("Must implement `get_response_schema`")

    def to_response_schema(self, **kwargs):
        _schema_type = self.get_response_schema()
        return _schema_type(**self.model_dump(), **kwargs)


class SuccessMessageMixin(Schema):
    message: str = "success"


# Message Types


class SuccessOutputSchema(SuccessMessageMixin):
    pass


# Model Schemas


class AuthUserSchema(ModelSchema):
    class Meta:
        model = UserModel
        exclude = ["password"]


# Base Schemas


class PasswordResetBase(InputSchemaMixin):
    new_password1: SecretStr
    new_password2: SecretStr

    @model_validator(mode="after")
    def check_passwords_match(self) -> "PasswordResetBase":
        if (
            self.new_password1
            and self.new_password2
            and self.new_password1 != self.new_password2
        ):
            raise exceptions.ValidationError("passwords do not match")
        return self

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return SuccessOutputSchema


# Input/Output Schemas

# Login


class LoginOutputSchema(SuccessMessageMixin):
    user: AuthUserSchema


class LoginInputSchema(InputSchemaMixin):
    _user: Optional[AbstractUser] = None
    username: str
    password: SecretStr

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return LoginOutputSchema

    @model_validator(mode="after")
    def check_user_exists(self):
        self._user = authenticate(
            username=self.username, password=self.password.get_secret_value()
        )
        if self._user is None:
            raise exceptions.AuthenticationFailed("Incorrect Credentials")
        return self


# Password Reset Request


class PasswordResetRequestInputSchema(InputSchemaMixin):
    email: EmailStr
    _form: Optional[PasswordResetForm] = None

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return SuccessOutputSchema

    @model_validator(mode="after")
    def check_email_form(self):
        self._form = PasswordResetForm(self.dict())
        if not self._form.is_valid():
            raise exceptions.ValidationError("Incorrect Email Format")
        return self


# Password Reset


class PasswordResetConfirmInputSchema(PasswordResetBase):
    token: str
    uid: str
    _form: Optional[SetPasswordForm] = None

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return SuccessOutputSchema

    @model_validator(mode="after")
    def check_reset_email(self):
        try:
            uid = force_str(uid_decoder(self.uid))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise exceptions.ValidationError("Invalid UID")
        if not default_token_generator.check_token(user, self.token):
            raise exceptions.ValidationError("Invalid Token")
        self._form = SetPasswordForm(
            user,
            dict(
                new_password1=self.new_password1.get_secret_value(),
                new_password2=self.new_password2.get_secret_value(),
            ),
        )
        if not self._form.is_valid():
            raise exceptions.ValidationError("Password Validation Failed")
        self._form.save()
        return self


# Change Password


class PasswordChangeInputSchema(PasswordResetBase):
    username: str
    old_password: SecretStr
    _form: Optional[PasswordChangeForm] = None

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return SuccessOutputSchema

    @model_validator(mode="after")
    def check_change_password(self):
        user = authenticate(
            username=self.username, password=self.old_password.get_secret_value()
        )
        self._form = PasswordChangeForm(
            user,
            dict(
                old_password=self.old_password.get_secret_value(),
                new_password1=self.new_password1.get_secret_value(),
                new_password2=self.new_password2.get_secret_value(),
            ),
        )
        if not self._form.is_valid():
            raise exceptions.ValidationError("Form Validation Failed")
        self._form.save()
        return self
