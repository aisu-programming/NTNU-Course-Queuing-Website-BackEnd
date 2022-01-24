''' Libraries '''
import base64
from flask import Blueprint

from exceptions import *
from api.utils.request import Request
from api.utils.response import *
from database.model import CourseObject


''' Settings '''
__all__ = ["login_required", "search_api"]
search_api = Blueprint("search_api", __name__)



''' Functions '''
@search_api.route("/", methods="POST")
@Request.json("course_id: str", "course_name: str", "departments: str", "time: str", "precise: bool")
def search_course(course_id, course_name, departments, time, precise):
    try:
        departments = base64.b64decode(departments.encode("utf-8")).decode("utf-8")
        time = base64.b64decode(time.encode("utf-8")).decode("utf-8")
        time_1, time_2 = time[:45], time[45:]
        courses = CourseObject.query.filter(CourseObject.time_1.op('&')(time_1) > 0)
        courses = CourseObject.query.filter_by(student_id=student_id).first().original_password
        return HTTPResponse("Success.", data={})
    except PasswordWrongException:
        return HTTPError("Id or password incorrect.", 403)
    except Exception as ex:
        return HTTPError(str(ex), 404)