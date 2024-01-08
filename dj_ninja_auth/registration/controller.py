from ninja_extra import ControllerBase, api_controller, http_post
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
        return new_user._form.save()


@api_controller("/account", permissions=[IsAuthenticated], tags=["account"])
class NinjaAuthAccountController(
    AccountController,
):
    auto_import = False
