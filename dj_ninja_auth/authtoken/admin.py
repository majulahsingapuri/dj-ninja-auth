from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import TokenModel

User = get_user_model()


class TokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created")
    fields = ("user",)
    search_fields = ("user__username",)
    search_help_text = "Username"
    ordering = ("-created",)
    actions = None  # Actions not compatible with mapped IDs.
    autocomplete_fields = ("user",)


admin.site.register(TokenModel, TokenAdmin)
