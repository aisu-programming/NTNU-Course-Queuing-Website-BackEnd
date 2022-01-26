''' Libraries '''
# import os
from functools import wraps
# from datetime import timedelta
from flask import Blueprint, request

from exceptions import *
from api.utils.request import Request
from api.utils.response import *
from api.utils.jwt import jwt_decode
from api.model import User
# from database.model import UserObject


''' Settings '''
__all__ = ["login_required", "auth_api"]
auth_api = Blueprint("auth_api", __name__)



''' Functions '''
def login_required(func):
    '''
    Check if the user is login
    Returns:
        - A wrapped function
        - 403 Not logged in
        - 403 Invalid token
        - 403 Authorization expired
    '''
    @wraps(func)
    @Request.cookies(vars_dict={"token": "jwt"})
    def wrapper(token, *args, **kwargs):
        if token is None:
            return HTTPError("Not logged in.", 403)
        json = jwt_decode(token)
        if json is None:
            return HTTPError("JWT token invalid.", 403)
        # student_id = json["data"]["student_id"]
        # password   = UserObject.query.filter_by(student_id=student_id).first().original_password
        # User(student_id, password)
        # kwargs["user"] = User(student_id, password)
        return func(*args, **kwargs)

    return wrapper


@auth_api.route("/session", methods=["GET", "POST"])
def session():

    # @login_required
    def logout():
        cookies = { "jwt": None }
        return HTTPResponse("Goodbye!", cookies=cookies)

    @Request.json("student_id: str", "password: str")
    def login(student_id, password):
        try:
            student_id = student_id.upper()
            user = User(student_id, password)
            cookies = { "jwt": user.jwt }
            return HTTPResponse("Success.", cookies=cookies)
        except PasswordWrongException:
            return HTTPError("Id or password incorrect.", 403)
        except Exception as ex:
            return HTTPError(str(ex), 404)

    methods = { "GET": logout, "POST": login }
    return methods[request.method]()