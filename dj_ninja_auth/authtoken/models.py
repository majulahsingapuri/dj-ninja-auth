import binascii
import os
from typing import Any, Type

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string

from . import app_settings


class TokenQuerySet(models.query.QuerySet):
    def get(self, *args: Any, **kwargs: Any) -> Any:
        token = super().get(*args, **kwargs)
        if token.created < timezone.now() - app_settings.EXPIRY:
            token.regenerate_key()
        return token


class TokenManager(models.Manager.from_queryset(TokenQuerySet)):
    pass


class Token(models.Model):
    """
    The default authorization token model.
    """

    objects = TokenManager()

    key = models.CharField(max_length=40)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="auth_token", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = "dj_ninja_auth.authtoken" not in settings.INSTALLED_APPS

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def regenerate_key(self):
        self.key = self.generate_key()
        self.save(update_fields=["key"])

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


TokenModel: Type[Token] = import_string(app_settings.MODEL)
