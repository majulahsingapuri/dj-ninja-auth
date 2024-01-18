# Django Ninja Auth

A one stop shop for all your Django-Ninja Authentication needs.
Supports REST authentication with Sessions, Auth Tokens and JWTs.

Fully Customisable to suit your needs.

This repository does not fix any issues in SimpleJWT or django-ninja-jwt.
It is intended to build upon the repository and add other forms of authentication on top of just JWTs

- [Django Ninja Auth](#django-ninja-auth)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Setup](#setup)
      - [NinjaAPI](#ninjaapi)
  - [Authentication](#authentication)
    - [Session](#session)
    - [Token](#token)
    - [JWT](#jwt)
  - [Registration](#registration)
  - [Allauth](#allauth)
    - [Installation](#installation-1)
    - [Social Authentication](#social-authentication)
  - [Customisation](#customisation)
    - [Schema](#schema)
    - [Controller](#controller)

## Getting Started

### Installation

To install the base library, run the following command:

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

4. Add the following to your `settings.py`

    ```python [settings.py]
    NINJA_AUTH_PASSWORD_RESET_URL = "http://localhost:8000/<YOUR_PASSWORD_RESET_FRONTEND_URL>/"
    ```

This will give you 5 basic endpoints that are not secured and can be called by anyone.
The endpoints are

- `/auth/login`
- `/auth/logout`
- `/auth/password/reset/request`
- `/auth/password/reset/confirm`
- `/auth/password/change`

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

```python [api.py]
from ninja_extra import NinjaExtraAPI
from dj_ninja_auth.authtoken.authentication import AccessTokenAuth
from dj_ninja_auth.authtoken.controller import NinjaAuthTokenController

api = NinjaExtraAPI(auth=[AccessTokenAuth()])
api.register_controllers(NinjaAuthTokenController)
```

### JWT

```python [api.py]
from ninja_extra import NinjaExtraAPI
from dj_ninja_auth.jwt.authentication import JWTAuth
from dj_ninja_auth.jwt.controller import NinjaAuthJWTController

api = NinjaExtraAPI(auth=[JWTAuth()])
api.register_controllers(NinjaAuthJWTController)
```

The JWT controller provides 2 additional endpoints for tokens.

- `/auth/refresh`
- `/auth/verify`

## Registration

To manage accounts in addition to the authentication functionality, use the `NinjaAuthAccountController` as below:

```python [api.py]
from ninja_extra import NinjaExtraAPI

from dj_ninja_auth.jwt.authentication import JWTAuth
from dj_ninja_auth.jwt.controller import NinjaAuthJWTController
from dj_ninja_auth.registration.controller import NinjaAuthAccountController

api = NinjaExtraAPI(auth=[JWTAuth()], csrf=True)
api.register_controllers(NinjaAuthJWTController, NinjaAuthAccountController)
```

This will provide the following endpoints.

- `/account/`: Allowed methods are `POST`, `PATCH` and `DELETE`.
- `/account/verify`
- `/account/resend-email`

## Allauth

This library is fully compatible with `allauth`, albeit there are some modifications to work in a REST-ful format.

### Installation

To include the `allauth` library for additional account management and social authentication, run the following command:

```bash
pip install dj-ninja-auth[allauth]
```

Add the following to your `settings.py`.

```python [settings.py]
# Specify the context processors as follows:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Already defined Django-related contexts here

                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    ...
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
    ...
]

INSTALLED_APPS = [
    ...
    # The following apps are required:
    'django.contrib.auth',
    'django.contrib.messages',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    'allauth.socialaccount.providers.agave',
    'allauth.socialaccount.providers.amazon',
    ...
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
)

# The following is necessary to bypass the default templates
ACCOUNT_ADAPTER = "dj_ninja_auth.registration.adapter.NinjaAccountAdapter"
NINJA_AUTH_EMAIL_CONFIRMATION_URL = "http://localhost:8000/confirm-email/"
```

**NOTE:** You do not need to include the allauth URLs in your `urls.py` as the functionality will automatically be present in `dj-ninja-auth`.

Once you have configured your `settings.py`, run the migrate command to add all the `allauth` migrations to your database.

```bash
python manage.py migrate
```

### Social Authentication

Social Authentication requires that you set up a [CSRF endpoint](#session) as this is required by `allauth`'s authentication endpoints.

You will then have to register your app in the `admin` console. Do remember to add the provdier to the `INSTALLED_APPS` else your provider will not show up in the admin console.

The next step is to set up your `urls.py` file so that the registered providers' urls are available.
To do so, add the following to your `urls.py`.
You can use any url prefix.
I chose to use the `social/` prefix for ease of use and to deconflict it with the `account/` url in the `NinjaAuthAccountController`.

```python [urls.py]
from django.contrib import admin
from django.urls import include, path

from .api import api

from allauth.urls import provider_urlpatterns # <-----

urlpatterns = [
    path("admin/", admin.site.urls),
    path("social/", include(provider_urlpatterns)), # <-----
    path("", api.urls),
]
```

After getting your CSRF token, setting up your `url.py` and registering your `SocialApplication`, you have to send a `X-WWW-FORM-URLENCODED` request to your desired provider's login endpoint.
A sample request is provided below.
Take note of the callback urls as stated in the `allauth` documentation.

```curl
curl --location 'http://127.0.0.1:8000/social/<PROVIDER>/login/' \
--header 'Cookie: csrftoken=<CSRF_TOKEN_VALUE>' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'csrfmiddlewaretoken=<CSRF_TOKEN_VALUE>'
```

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
