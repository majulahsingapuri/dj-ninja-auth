from django.contrib.auth import login as django_login
from ninja_extra import ControllerBase, api_controller, http_post
from ninja_extra.permissions import AllowAny

from ..controller import (
    AuthenticationController,
    PasswordChangeController,
    PasswordResetController,
    UserController,
)
from ..schema_control import SchemaControl
from .schema_control import JWTSchemaControl

schema = SchemaControl()
jwt_schema = JWTSchemaControl()


class JWTAuthenticationController(AuthenticationController):
    auto_import = False

    @http_post(
        "/login",
        response={200: jwt_schema.pair_schema.get_response_schema()},
        auth=None,
        url_name="login",
    )
    def login(self, credentials: jwt_schema.pair_schema):
        """Logs in a user

        Args:
            credentials (schema.login_schema): The log in Credentials, typically username and/or email, and password

        Returns:
            JSON: A JSON object with the user's details
        """
        credentials.post_validate_schema()
        django_login(self.context.request, credentials._user)
        kwargs = {
            "user": credentials._user,
            "access": credentials._access,
            "refresh": credentials._refresh,
        }
        return credentials.to_response_schema(**kwargs)


class JWTTokenVerificationController(ControllerBase):
    auto_import = False

    @http_post(
        "/verify",
        response={200: schema.success_schema},
        url_name="token_verify",
    )
    def verify_token(self, token: jwt_schema.verify_schema):
        """Verifies that the provided token is valid.

        Args:
            token (jwt_schema.verify_schema): The `access` or `refresh` token.

        Returns:
            JSON: A success object if the token is valid.
        """
        return token.to_response_schema()


class JWTTokenRefreshController(ControllerBase):
    auto_import = False

    @http_post(
        "/refresh",
        response={200: jwt_schema.refresh_schema.get_response_schema()},
        url_name="token_refresh",
        auth=None,
    )
    def refresh_token(self, token: jwt_schema.refresh_schema):
        """Consumes a refresh token and returns a new `access`, `refresh` token pair.

        Args:
            token (jwt_schema.refresh_schema): The `refresh` token.

        Returns:
            JSON: A JSON object with the new tokens
        """
        return token.to_response_schema()


@api_controller("/auth", permissions=[AllowAny], tags=["auth"])
class NinjaAuthJWTController(
    JWTAuthenticationController,
    PasswordResetController,
    PasswordChangeController,
    JWTTokenRefreshController,
    JWTTokenVerificationController,
    UserController,
):
    auto_import = False
