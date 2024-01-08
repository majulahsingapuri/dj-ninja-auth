from ninja_extra import NinjaExtraAPI

from dj_ninja_auth.jwt.authentication import JWTAuth
from dj_ninja_auth.jwt.controller import NinjaAuthJWTController
from dj_ninja_auth.registration.controller import NinjaAuthAccountController

api = NinjaExtraAPI(auth=[JWTAuth()])
api.register_controllers(NinjaAuthJWTController, NinjaAuthAccountController)
