from django.conf import settings
from ninja_extra import (
    ControllerBase,
    api_controller,
    exceptions,
    http_delete,
    http_patch,
    http_post,
)
from ninja_extra.permissions import AllowAny, IsAuthenticated

from ..schema_control import SchemaControl
from .schema_control import RegistrationSchemaControl

allauth_enabled = "allauth" in settings.INSTALLED_APPS
if allauth_enabled:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
    from allauth.account.utils import send_email_confirmation

schema = SchemaControl()
registration_schema = RegistrationSchemaControl()


class AccountController(ControllerBase):
    auto_import = False

    @http_post(
        "/",
        response={200: registration_schema.create_user_schema.get_response_schema()},
        permissions=[AllowAny],
        auth=None,
        url_name="create_user",
    )
    def post_create_user(self, new_user: registration_schema.create_user_schema):
        user = new_user.save(self.context.request)
        if (
            allauth_enabled
            and allauth_account_settings.EMAIL_VERIFICATION
            != allauth_account_settings.EmailVerificationMethod.NONE
        ):
            send_email_confirmation(self.context.request, user, True)
        return user

    @http_patch(
        "/",
        response={200: schema.auth_user_schema},
        permissions=[IsAuthenticated],
        url_name="update_user",
    )
    def patch_update_user(self, update_user: registration_schema.update_user_schema):
        user = self.context.request.auth
        for k, v in update_user.model_dump().items():
            if v:
                setattr(user, k, v)
        user.save()
        return user

    @http_delete(
        "/",
        response={200: schema.success_schema},
        permissions=[IsAuthenticated],
        url_name="delete_user",
    )
    def delete_user(self):
        user = self.context.request.auth
        user.is_active = False
        user.save()
        return schema.success_schema()

    if allauth_enabled:

        @http_post(
            "/verify",
            response={
                200: registration_schema.verify_email_schema.get_response_schema()
            },
            permissions=[AllowAny],
            auth=None,
            url_name="verify_email",
        )
        def post_verify_email(
            self, verify_email: registration_schema.verify_email_schema
        ):
            emailconfirmation = EmailConfirmationHMAC.from_key(verify_email.key)
            if not emailconfirmation:
                queryset = EmailConfirmation.objects.all_valid().select_related(
                    "email_address__user"
                )
                try:
                    emailconfirmation = queryset.get(key=verify_email.key.lower())
                except EmailConfirmation.DoesNotExist:
                    raise exceptions.NotFound("Invalid Key")
            emailconfirmation.confirm(self.context.request)
            return verify_email.to_response_schema()

        @http_post(
            "/resend-email",
            response={
                200: registration_schema.resend_email_schema.get_response_schema()
            },
            permissions=[AllowAny],
            auth=None,
            url_name="resend_email",
        )
        def post_resend_email(
            self, resend_email: registration_schema.resend_email_schema
        ):
            if (
                allauth_account_settings.EMAIL_VERIFICATION
                != allauth_account_settings.EmailVerificationMethod.NONE
                and resend_email._user
            ):
                send_email_confirmation(self.context.request, resend_email._user)
            return resend_email.to_response_schema()


@api_controller("/account", permissions=[IsAuthenticated], tags=["account"])
class NinjaAuthAccountController(
    AccountController,
):
    auto_import = False
