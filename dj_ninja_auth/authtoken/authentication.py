from typing import Any, Type

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.http import HttpRequest
from ninja_extra import exceptions
from ninja_extra.security import HttpBearer


class AccessTokenBaseAuthentication:
    def __init__(self) -> None:
        super().__init__()
        self.user_model = get_user_model()

    def get_user(self, token) -> Type[AbstractUser]:
        """
        Attempts to find and return a user using the given token.
        """

        try:
            user = self.user_model.objects.get(auth_token__key=token)
        except self.user_model.DoesNotExist as e:
            raise exceptions.AuthenticationFailed("User not found") from e

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")

        return user

    def access_token_authenticate(
        self, request: HttpRequest, token: str
    ) -> Type[AbstractUser]:
        request.user = AnonymousUser()
        user = self.get_user(token)
        request.user = user
        return user


class AccessTokenAuth(AccessTokenBaseAuthentication, HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Any | None:
        return self.access_token_authenticate(request, token)
