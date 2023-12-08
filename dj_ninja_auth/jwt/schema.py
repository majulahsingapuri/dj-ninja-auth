from typing import Dict, Optional, Type, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, update_last_login
from ninja import Schema
from pydantic import model_validator

from ..schema import InputSchemaMixin, LoginInputSchema, LoginOutputSchema
from . import app_settings
from .exceptions import exceptions
from .tokens import RefreshToken, UntypedToken
from .utils import token_error

user_name_field = get_user_model().USERNAME_FIELD  # type: ignore


class JWTTokenInputSchemaMixin:
    def check_user_authentication_rule(self) -> None:
        if not app_settings.USER_AUTHENTICATION_RULE(self._user):
            raise exceptions.AuthenticationFailed(
                self._default_error_messages["no_active_account"]
            )

    @classmethod
    def get_token(cls, user: AbstractUser) -> Dict:
        raise NotImplementedError(
            "Must implement `get_token` method for `TokenInputSchemaMixin` subclasses"
        )


class TokenInputSchemaBase(JWTTokenInputSchemaMixin, LoginInputSchema):
    _access: Optional[str]
    _refresh: Optional[str]

    def post_validate_schema(self) -> dict:
        """
        This is a post validate process which is common for any token generating schema.
        :param values:
        :return:
        """
        # get_token can return values that wants to apply to `OutputSchema`

        data = self.get_token(self._user)

        if not isinstance(data, dict):
            raise Exception("`get_token` must return a `typing.Dict` type.")

        if app_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self._user)

        self._access = data["access"]
        self._refresh = data["refresh"]

    @classmethod
    def get_response_schema(cls) -> type[Schema]:
        return TokenPairOutputSchema


class TokenPairOutputSchema(LoginOutputSchema):
    access: str
    refresh: str


class TokenPairInputSchema(TokenInputSchemaBase):
    @classmethod
    def get_token(cls, user: AbstractUser) -> Dict:
        values = {}
        refresh = RefreshToken.for_user(user)
        refresh = cast(RefreshToken, refresh)
        values["refresh"] = str(refresh)
        values["access"] = str(refresh.access_token)
        return values


class TokenRefreshInputSchema(InputSchemaMixin):
    refresh: str

    @model_validator(mode="after")
    def validate_schema(self) -> dict:
        if not self.refresh:
            raise exceptions.ValidationError({"refresh": "token is required"})
        return self

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return TokenRefreshOutputSchema


class TokenRefreshOutputSchema(Schema):
    refresh: str
    access: Optional[str] = None

    @model_validator(mode="after")
    @token_error
    def validate_schema(self) -> dict:
        if not self.refresh:
            raise exceptions.ValidationError({"refresh": "refresh token is required"})

        refresh = RefreshToken(self.refresh)

        self.access = str(refresh.access_token)
        return self


class TokenVerifyInputSchema(InputSchemaMixin):
    token: str

    @model_validator(mode="after")
    @token_error
    def validate_schema(self) -> dict:
        if not self.token:
            raise exceptions.ValidationError({"token": "token is required"})
        UntypedToken(self.token)
        return self

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return Schema

    def to_response_schema(self):
        return {}
