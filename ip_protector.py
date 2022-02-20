''' Configurations '''
import os
from dotenv import load_dotenv
load_dotenv(".config/flask.env")
load_dotenv(".config/validation.env")
os.environ["ROOT_PATH"] = os.path.dirname(os.path.abspath(__file__))



''' Libraries '''
# Flask
from flask import Flask

from utils.exceptions import *
from ntnu.utils.webdriver import login_course_taking_system
from api.utils.request import Request
from api.utils.response import HTTPResponse, HTTPError



''' Settings '''
app = Flask(__name__)
from utils.my_logging import *
import logging
ip_protector_logger = logging.getLogger(name="ip_protector")



''' Functions '''
@app.route("/login", methods=["POST"])
@Request.json("student_id: str", "password: str")
def login(student_id, password):

    ip_protector_logger.info(f"User '{student_id}' is trying to login.")

    try:
        cookies, name, major = login_course_taking_system(student_id, password)
        ip_protector_logger.info(f"User '{student_id}' has successfully logged in.")
        return HTTPResponse("Success.", data={
            "cookies": cookies,
            "name"   : name,
            "major"  : major
        })

    except PasswordWrongException:
        ip_protector_logger.info(f"User '{student_id}' has failed to login: Password wrong.")
        return HTTPError("Password wrong.", 403)

    except StudentIdNotExistException:
        ip_protector_logger.info(f"User '{student_id}' has failed to login: Student ID not exist.")
        return HTTPError("Student ID not exist.", 403)

    except SeleniumStuckException:
        ip_protector_logger.info(f"User '{student_id}' has failed to login: Selenium stucked.")
        return HTTPError("Selenium stucked.", 500)

    except Exception as ex:
        ip_protector_logger.info(f"User '{student_id}' has failed to login: {str(ex)}.")
        return HTTPError(str(ex), 404)


@app.route("/take", methods=["POST"])
@Request.json("student_id: str", "password: str", "take_course: bool",
              "course_no: str", "domain: str", "year: int")
def take_course(student_id, password, take_course,
                course_no, domain, year):

    ip_protector_logger.info(f"User '{student_id}' is trying to take course {course_no} (domain: {domain}).")

    try:
        result = login_course_taking_system(student_id, password, take_course,
                                            course_no, domain, year)
        ip_protector_logger.info(f"User '{student_id}' has successfully finished the taking process.")
        return HTTPResponse("Success.", data={"result": result})

    except PasswordWrongException:
        ip_protector_logger.info(f"User '{student_id}' has failed to take course: Password wrong.")
        return HTTPError("Password wrong.", 403)

    except StudentIdNotExistException:
        ip_protector_logger.info(f"User '{student_id}' has failed to take course: Student ID not exist.")
        return HTTPError("Student ID not exist.", 403)

    except SeleniumStuckException:
        ip_protector_logger.info(f"User '{student_id}' has failed to take course: Selenium stucked.")
        return HTTPError("Selenium stucked.", 500)

    except Exception as ex:
        ip_protector_logger.info(f"User '{student_id}' has failed to take course: {str(ex)}.")
        return HTTPError(str(ex), 404)



''' Run '''
app.run("0.0.0.0", port=5500)