from typing import Optional, Type

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import AbstractUser
from django.forms import Form
from django.utils.encoding import force_str
from ninja import ModelSchema, Schema
from ninja_extra import exceptions
from pydantic import EmailStr, SecretStr, model_validator

allauth_enabled = "allauth" in settings.INSTALLED_APPS
if allauth_enabled:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.forms import default_token_generator
    from allauth.account.utils import url_str_to_user_pk as uid_decoder

    from .forms import AllAuthPasswordResetForm
else:
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode as uid_decoder

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


# TODO: restructure the code somehow such that there is no circular import and changing the schema_control will change this as well.
class LoginOutputSchema(SuccessMessageMixin):
    user: AuthUserSchema


class LoginInputSchema(InputSchemaMixin):
    _user: Optional[AbstractUser] = None
    if (
        not allauth_enabled
        or allauth_account_settings.AUTHENTICATION_METHOD
        == allauth_account_settings.AuthenticationMethod.USERNAME
    ):
        username: str
    elif (
        allauth_account_settings.AUTHENTICATION_METHOD
        == allauth_account_settings.AuthenticationMethod.EMAIL
    ):
        email: EmailStr
    else:
        username: Optional[str] = None
        email: Optional[EmailStr] = None
    password: SecretStr

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return LoginOutputSchema

    @model_validator(mode="after")
    def check_user_exists(self):
        self._user = authenticate(
            username=getattr(self, "username", None),
            email=getattr(self, "email", None),
            password=self.password.get_secret_value(),
        )
        if self._user is None:
            raise exceptions.AuthenticationFailed("Incorrect Credentials")
        if (
            allauth_enabled
            and allauth_account_settings.EMAIL_VERIFICATION
            == allauth_account_settings.EmailVerificationMethod.MANDATORY
            and not self._user.emailaddress_set.filter(
                email=self._user.email, verified=True
            ).exists()
        ):
            raise exceptions.AuthenticationFailed("Email is not verified")
        return self


# Password Reset Request


class PasswordResetRequestInputSchema(InputSchemaMixin):
    email: EmailStr
    _form: Optional[Form] = None

    def get_form(self):
        if allauth_enabled:
            return AllAuthPasswordResetForm
        return PasswordResetForm

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return SuccessOutputSchema

    @model_validator(mode="after")
    def check_email_form(self):
        self._form = self.get_form()(self.dict())
        if not self._form.is_valid():
            raise exceptions.ValidationError(self._form.errors)
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
            raise exceptions.ValidationError(self._form.errors)
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
        if not user:
            raise exceptions.AuthenticationFailed()
        self._form = PasswordChangeForm(
            user,
            dict(
                old_password=self.old_password.get_secret_value(),
                new_password1=self.new_password1.get_secret_value(),
                new_password2=self.new_password2.get_secret_value(),
            ),
        )
        if not self._form.is_valid():
            raise exceptions.ValidationError(self._form.errors)
        self._form.save()
        return self
