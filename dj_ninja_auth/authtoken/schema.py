from typing import Type

from ninja import Schema

from ..schema import LoginInputSchema, LoginOutputSchema
from .models import TokenModel


class AuthTokenLoginOutputSchema(LoginOutputSchema):
    token: str


class AuthTokenLoginInputSchema(LoginInputSchema):
    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return AuthTokenLoginOutputSchema

    def to_response_schema(self, **kwargs):
        token, _ = TokenModel.objects.get_or_create(user=self._user)
        kwargs["token"] = token.key
        return super().to_response_schema(**kwargs)
