from rest_framework import permissions
from rest_framework.exceptions import APIException
from decouple import config
from webapi.models import userwhitelistToken, whitelistToken
import jwt


class authorization(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            token_catch = request.META["HTTP_AUTHORIZATION"][7:]
            request.GET._mutable = True
            my_token = jwt.decode(
                token_catch, config("User_jwt_token"), algorithms=["HS256"]
            )
            request.GET["token"] = my_token
            userwhitelistToken.objects.get(user=my_token["id"], token=token_catch)
            return True

        except:
            raise NeedLogin()


class adminauthorization(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            token_catch = request.META["HTTP_AUTHORIZATION"][7:]
            request.GET._mutable = True
            my_token = jwt.decode(
                token_catch, config("Superadmin_jwt_token"), algorithms=["HS256"]
            )
            request.GET["token"] = my_token
            whitelistToken.objects.get(user=my_token["id"], token=token_catch)
            return True

        except:
            raise NeedLogin()


class NeedLogin(APIException):
    status_code = 401
    default_detail = {"status": False, "message": "Unauthorized"}
    default_code = "not_authenticated"
