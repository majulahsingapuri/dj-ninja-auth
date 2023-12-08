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

from .schema import AuthUserSchema
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
        reset_request._form.save(request=self.context.request)
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
        return passwords.to_response_schema()


class UserController(ControllerBase):
    auto_import = False

    @http_get(
        "/me",
        permissions=[IsAuthenticated],
        response={200: AuthUserSchema},
        url_name="get_user",
    )
    def get_me(self):
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
