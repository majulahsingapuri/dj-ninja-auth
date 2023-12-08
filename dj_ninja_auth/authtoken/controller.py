from django.contrib.auth import login as django_login
from ninja_extra import api_controller, http_post
from ninja_extra.permissions import AllowAny

from ..controller import (
    AuthenticationController,
    PasswordChangeController,
    PasswordResetController,
    UserController,
)
from .schema_control import AuthTokenSchemaControl

schema = AuthTokenSchemaControl()


class TokenAuthenticationController(AuthenticationController):
    auto_import = False

    @http_post(
        "/login",
        response={200: schema.token_login_schema.get_response_schema()},
        auth=None,
        url_name="login",
    )
    def login(self, credentials: schema.token_login_schema):
        django_login(self.context.request, credentials._user)
        return credentials.to_response_schema(user=credentials._user)


@api_controller("/auth", permissions=[AllowAny], tags=["auth"])
class NinjaAuthTokenController(
    TokenAuthenticationController,
    PasswordResetController,
    PasswordChangeController,
    UserController,
):
    auto_import = False
