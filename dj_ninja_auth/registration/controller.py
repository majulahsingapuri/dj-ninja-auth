from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_patch,
    http_post,
)
from ninja_extra.permissions import AllowAny, IsAuthenticated

from ..schema_control import SchemaControl
from .schema_control import RegistrationSchemaControl

schema = SchemaControl()
registration_schema = RegistrationSchemaControl()


class AccountController(ControllerBase):
    auto_import = False

    @http_post(
        "/",
        response={200: schema.auth_user_schema},
        permissions=[AllowAny],
        auth=None,
        url_name="create_user",
    )
    def post_create_user(self, new_user: registration_schema.create_user_schema):
        return new_user.save(self.context.request)

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


@api_controller("/account", permissions=[IsAuthenticated], tags=["account"])
class NinjaAuthAccountController(
    AccountController,
):
    auto_import = False
