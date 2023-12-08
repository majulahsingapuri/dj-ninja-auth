from typing import Any, Type

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.http import HttpRequest
from django.utils.module_loading import import_string
from ninja_extra.security import HttpBearer

from . import app_settings
from .exceptions import AuthenticationFailed, InvalidToken, TokenError
from .tokens import Token


class JWTBaseAuthentication:
    def __init__(self) -> None:
        super().__init__()
        self.user_model = get_user_model()

    @classmethod
    def get_validated_token(cls, raw_token) -> Type[Token]:
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in app_settings.TOKEN_CLASSES:
            AuthToken = import_string(AuthToken)
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": "Given token not valid for any token type",
                "messages": messages,
            }
        )

    def get_user(self, validated_token) -> Type[AbstractUser]:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[app_settings.USER_ID_CLAIM]
        except KeyError as e:
            raise InvalidToken(
                "Token contained no recognizable user identification"
            ) from e

        try:
            user = self.user_model.objects.get(**{app_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist as e:
            raise AuthenticationFailed("User not found") from e

        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        return user

    def jwt_authenticate(self, request: HttpRequest, token: str) -> Type[AbstractUser]:
        request.user = AnonymousUser()
        validated_token = self.get_validated_token(token)
        user = self.get_user(validated_token)
        request.user = user
        return user


class JWTAuth(JWTBaseAuthentication, HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Any:
        return self.jwt_authenticate(request, token)


def default_user_authentication_rule(user) -> bool:
    return user is not None and user.is_active
