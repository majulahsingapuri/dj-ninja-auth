from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_generic,
    http_get,
    http_post,
)
from ninja_extra.permissions import AllowAny, IsAuthenticated

from . import app_settings
from .schema_control import SchemaControl

schema = SchemaControl()


class AuthenticationController(ControllerBase):
    auto_import = False

    @http_post(
        "/login",
        response={200: schema.login_schema.get_response_schema()},
        auth=None,
        url_name="login",
    )
    def login(
        self,
        credentials: schema.login_schema,
    ):
        """Logs in a user

        Args:
            credentials (schema.login_schema): The log in Credentials, typically username and/or email, and password

        Returns:
            JSON: A JSON object with the user's details
        """
        django_login(self.context.request, credentials._user)
        kwargs = {"user": credentials._user}
        return credentials.to_response_schema(**kwargs)

    @http_generic(
        "/logout",
        methods=["POST"],
        permissions=[IsAuthenticated],
        response={200: schema.success_schema},
        url_name="logout",
    )
    def logout(self):
        """Logs out the user by flushing session data from the request

        Returns:
            JSON: A success message for a logged out user
        """
        django_logout(self.context.request)
        return schema.success_schema()


class PasswordResetController(ControllerBase):
    auto_import = False

    @http_post(
        "/password/reset/request",
        response={200: schema.password_reset_request_schema.get_response_schema()},
        auth=None,
        url_name="password_reset_request",
    )
    def password_reset_request(
        self, reset_request: schema.password_reset_request_schema
    ):
        """Requests for a password reset on behalf of an unauthenticated user

        Args:
            reset_request (schema.password_reset_request_schema): The user's email address

        Returns:
            JSON: A success message to show confirmation of receipt of the request, regardless of the existence of the email in the database.
        """
        reset_request._form.save(
            request=self.context.request,
            email_template_name="password/reset_email.html",
            extra_email_context={"password_reset_url": app_settings.PASSWORD_RESET_URL},
        )
        return reset_request.to_response_schema()

    @http_post(
        "/password/reset/confirm",
        response={200: schema.password_reset_confirm_schema.get_response_schema()},
        auth=None,
        url_name="password_reset_confirm",
    )
    def password_reset_confirm(
        self, reset_confirm: schema.password_reset_confirm_schema
    ):
        """Resets the user's password

        Args:
            reset_confirm (schema.password_reset_confirm_schema): The password reset parameters, typically the new credentials and a token that was sent to the user's email.

        Returns:
            JSON: A success message to indicate the password was changed successfully.
        """
        return reset_confirm.to_response_schema()


class PasswordChangeController(ControllerBase):
    auto_import = False

    @http_post(
        "/password/change",
        response={200: schema.password_change_schema.get_response_schema()},
        permissions=[IsAuthenticated],
        url_name="password_change",
    )
    def password_change(self, passwords: schema.password_change_schema):
        """A self-service for an authenticated user to change their own password

        Args:
            passwords (schema.password_change_schema): The user's credentials such as their `username`, `old_password` and 2 entries of their `new_password`.

        Returns:
            JSON: A success message to indicate the password has been changed successfully.
        """
        return passwords.to_response_schema()


class UserController(ControllerBase):
    auto_import = False

    @http_get(
        "/me",
        permissions=[IsAuthenticated],
        response={200: schema.auth_user_schema},
        url_name="get_user",
    )
    def get_me(self):
        """An endpoint that fetches the user's information.

        Returns:
            JSON: A JSON object of the user's information.
        """
        return self.context.request.auth


# For session Authentication, requires `csrf=True`. See https://github.com/vitalik/django-ninja/issues/8
@api_controller("/auth", permissions=[AllowAny], tags=["auth"])
class NinjaAuthDefaultController(
    AuthenticationController,
    PasswordResetController,
    PasswordChangeController,
    UserController,
):
    auto_import = False
