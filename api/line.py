''' Libraries '''
import logging
flask_logger = logging.getLogger(name="flask")
import requests
from flask import Blueprint, request

from exceptions import *
from api.auth import login_required
from api.utils.jwt import jwt_decode
from api.utils.response import *
from api.utils.rate_limit import rate_limit



''' Settings '''
__all__ = ["line_api"]
line_api = Blueprint("line_api", __name__)



''' Functions '''
@line_api.route("/callback", methods=["GET"])
@login_required
@rate_limit
def register_line(user):

    code = request.args.get("code")
    if code != None:
        try:
            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) trying to link LINE notification.")
            response = requests.post(
                "https://api.line.me/oauth2/v2.1/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type"   : "authorization_code",
                    "code"         : request.args.get("code"),
                    "redirect_uri" : "https://ntnu.site/api/line/callback",
                    "client_id"    : "1656899574",
                    "client_secret": "0abf5b230bd3a055976446df5bbe8d75",
                }
            )

            if response.ok:
                id_token = jwt_decode(token=response.json()["id_token"],
                                    jwt_secret="0abf5b230bd3a055976446df5bbe8d75",
                                    audience="1656899574",
                                    jwt_issuer="https://access.line.me")
                user.user.update_line(id_token["sub"])
                flask_logger.info(f"User '{user.student_id}' ({user.user.name}) has successfully linked LINE notification!")
            else:
                flask_logger.error(f"User '{user.student_id}' ({user.user.name}) has failured to link LINE notification: {response.text}")
            
        except DataIncorrectException as ex:
            logging.warning(f"DataIncorrectException: {str(ex)}")
            return HTTPError(str(ex), 403)

        except Exception as ex:
            logging.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)
    
    else:
        flask_logger.warning(f"User '{user.student_id}' ({user.user.name}) has cancelled to link LINE notification.")
    
    return HTTPRedirect("https://ntnu.site/rushlist/wait")
