# Django Ninja Auth

A one stop shop for all your Django-Ninja Authentication needs.
Supports REST authentication with Sessions, Auth Tokens and JWTs.

Fully Customisable to suit your needs.

This repository does not fix any issues in SimpleJWT or django-ninja-jwt.
It is intended to build upon the repository and add other forms of authentication on top of just JWTs

## Getting Started

### Installation

```bash
pip install dj-ninja-auth
```

### Setup

#### NinjaAPI

1. Create a `api.py` file in your app directory next to the `settings.py` and `urls.py` files.
2. Add the following lines of code to your `api.py`

    ```python [api.py]
    from ninja_extra import NinjaExtraAPI
    from dj_ninja_auth.controller import NinjaAuthDefaultController

    api = NinjaExtraAPI()
    api.register_controllers(NinjaAuthDefaultController)
    ```

3. Add the following lines to your `urls.py` file

    ```python [urls.py]
    from .api import api

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("", api.urls)
    ]
    ```

This will give you 5 basic endpoints that are not secured and can be called by anyone.
The endpoints are

- `/auth/login`
- `/auth/logout`
- `/auth/password/reset/request`
- `/auth/password/reset/confirm`
- `/auth/password/change`

#### Password Reset Template

Django's default email template requires a `password_reset_confirm` reverse url that is incompatible with Django Ninja's [namespace convention](https://django-ninja.dev/guides/urls/) and will throw [this error](https://github.com/iMerica/dj-rest-auth/issues/494) if not handled properly.
As a workaround, it is required that you provide your own email reset template.
You can place it anywhere in your project as long as you link it in your `settings.py`'s `TEMPLATES` variable.
In my example below, I have put it in the `{$project_root}/templates/` directory.

```python [settings.py]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": { ... },
    },
]
```

In your `templates` directory, create the following file at `templates/registration/password_reset_email.html` and **minimally** add the following.

```jinja [password_reset_email.html]
{% load i18n %}
{% autoescape off %}

    {% translate "Please go to the following page and choose a new password:" %}

    {% block reset_link %}
        http://{YOUR_DOMAIN_HERE}/{YOUR_FRONTEND_PASSWORD_RESET_ENDPOINT}?uid={{ uid }}&token={{ token }}
    {% endblock %}

{% endautoescape %}
```

**NOTE**: Replace `YOUR_DOMAIN_HERE` and `YOUR_FRONTEND_PASSWORD_RESET_ENDPOINT` with values that correspond to your setup.
The `uid` and `token` variables have to be passed to the backend for verification before the password can be changed.

## Authentication

There are 3 controllers that you can register in your `api.py` file for your application depending on your authentication needs.

### Session

The easiest way to use authentication is to use the Session Authentication.
Note that the `csrf=True` kwarg has to be passed in to allow Django Ninja to pass CSRF cookies for validation.
You will have to [provide your own endpoint](https://django-ninja.dev/reference/csrf/?h=csrf#django-ensure_csrf_cookie-decorator) to get a CSRF cookie from Ninja.

```python [api.py]
from ninja.security import django_auth
from dj_ninja_auth.controller import NinjaAuthDefaultController

api = NinjaExtraAPI(auth=[django_auth], csrf=True)
api.register_controllers(NinjaAuthDefaultController)
```

### Token

Since the `token`s will be stored in the database, you are required to add the `dj_ninja_auth.authtoken` app to your `INSTALLED_APPS` and migrate the database.

```python
from ninja_extra import NinjaExtraAPI
from dj_ninja_auth.authtoken.authentication import AccessTokenAuth
from dj_ninja_auth.authtoken.controller import NinjaAuthTokenController

api = NinjaExtraAPI(auth=[AccessTokenAuth()])
api.register_controllers(NinjaAuthTokenController)
```

### JWT

```python
from ninja_extra import NinjaExtraAPI
from dj_ninja_auth.jwt.authentication import JWTAuth
from dj_ninja_auth.jwt.controller import NinjaAuthJWTController

api = NinjaExtraAPI(auth=[JWTAuth()])
api.register_controllers(NinjaAuthJWTController)
```

The JWT controller provides 2 additional endpoints for tokens.

- `/auth/refresh`
- `/auth/verify`

## Customisation

Every aspect of the the `Schema`s and `Controller`s can be modified to suit your needs.

### Schema

Say for example you want to modify the output schema once the user logs in in your app `my_app` to only display specific fields.
In your `my_app.schema.py`, you can create the following:

```python [schema.py]
from django.contrib.auth import authenticate, get_user_model
from dj_ninja_auth.schema import SuccessMessageMixin, LoginInputSchema

UserModel = get_user_model()

class MyAuthUserSchema(ModelSchema):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'first_name', 'last_name']

class MyLoginOutputSchema(SuccessMessageMixin):
    user: MyAuthUserSchema
    my_other_value: str

class MyLoginInputSchema(LoginInputSchema):
    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return MyLoginOutputSchema

    def to_response_schema(self, **kwargs):
        return super().to_response_schema(my_other_value="foo", **kwargs)
```

Then in your `settings.py`, you can specify:

```python [settings.py]
NINJA_AUTH_LOGIN_INPUT_SCHEMA = "my_app.schema.MyLoginInputSchema"
```

### Controller

Say you wanted to add another endpoint to the default auth controller that is an authenticated route and returns the user's details in the schema defined above.
In your `controller.py`:

```python [controller.py]
from ninja_extra import ControllerBase, api_controller, http_get
from ninja_extra.permissions import IsAuthenticated

from .schema import MyAuthUserSchema

class UserController(ControllerBase):
    auto_import = False

    @http_get(
        "/me",
        permissions=[IsAuthenticated],
        response={200: MyAuthUserSchema},
        url_name="get_user",
    )
    def get_user(self):
        return MyAuthUserSchema(user=self.context.request.auth)

@api_controller("/auth", permissions=[AllowAny], tags=["auth"])
class MyNinjaAuthController(
    AuthenticationController,
    PasswordResetController,
    PasswordChangeController,
    UserController
):
    auto_import = False

```

Then in your `api.py`, replace the default controller with your custom controller

```python [api.py]
from ninja_extra import NinjaExtraAPI
from .controller import MyNinjaAuthController

api = NinjaExtraAPI()
api.register_controllers(MyNinjaAuthController)
```
