from dj_ninja_auth.jwt import app_settings

from .backends import TokenBackend

token_backend = TokenBackend(
    app_settings.ALGORITHM,
    app_settings.SIGNING_KEY,
    app_settings.VERIFYING_KEY,
    app_settings.AUDIENCE,
    app_settings.ISSUER,
    app_settings.JWK_URL,
    app_settings.LEEWAY,
)
