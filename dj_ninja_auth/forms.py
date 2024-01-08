from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from . import app_settings


def default_url_generator(uid, token):
    url = f"{app_settings.PASSWORD_RESET_URL}?uid={ uid }&token={ token }"
    return url


if "allauth" in settings.INSTALLED_APPS:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.forms import ResetPasswordForm as DefaultPasswordResetForm
    from allauth.account.forms import default_token_generator
    from allauth.account.utils import (
        filter_users_by_email,
        user_pk_to_url_str,
        user_username,
    )

    class AllAuthPasswordResetForm(DefaultPasswordResetForm):
        def clean_email(self):
            """
            Invalid email should not raise error, as this would leak users
            for unit test: test_password_reset_with_invalid_email
            """
            email = self.cleaned_data["email"]
            email = get_adapter().clean_email(email)
            self.users = filter_users_by_email(email, is_active=True)
            return self.cleaned_data["email"]

        def save(self, request, **kwargs):
            current_site = get_current_site(request)
            email = self.cleaned_data["email"]
            token_generator = kwargs.get("token_generator", default_token_generator)

            for user in self.users:

                temp_key = token_generator.make_token(user)

                # send the password reset email
                url_generator = kwargs.get("url_generator", default_url_generator)
                uid = user_pk_to_url_str(user)
                url = url_generator(uid, temp_key)

                context = {
                    "current_site": current_site,
                    "user": user,
                    "password_reset_url": url,
                    "request": request,
                    "token": temp_key,
                    "uid": uid,
                }
                if (
                    allauth_account_settings.AUTHENTICATION_METHOD
                    != allauth_account_settings.AuthenticationMethod.EMAIL
                ):
                    context["username"] = user_username(user)
                get_adapter(request).send_mail(
                    "account/email/password_reset_key", email, context
                )
            return self.cleaned_data["email"]
