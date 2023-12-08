from ninja_extra import NinjaExtraAPI

from dj_ninja_auth.jwt.authentication import JWTAuth
from dj_ninja_auth.jwt.controller import NinjaAuthJWTController

api = NinjaExtraAPI(auth=[JWTAuth()])
api.register_controllers(NinjaAuthJWTController)
