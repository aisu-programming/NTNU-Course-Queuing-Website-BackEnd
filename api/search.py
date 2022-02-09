''' Libraries '''
import base64
from flask import Blueprint
from bitstring import BitArray
from sqlalchemy import or_, and_

from exceptions import *
from api.utils.request import Request
from api.utils.response import *
from database.model import CourseObject



''' Settings '''
__all__ = ["login_required", "search_api"]
search_api = Blueprint("search_api", __name__)



''' Functions '''
@search_api.route("/", methods=["POST"])
@Request.json("id: str", "name: str", "department: str", "teacher: str", 
              "time: str", "place: int", "precise: bool")
def search_course(id, name, department, teacher, time, place, precise):

    try:

        # id
        if id != "" and len(id) != 4:
            raise DataIncorrectException("Id form incorrect.")

        # name
        name = name.strip()

        # department
        department = BitArray(base64.b64decode(department.encode("utf-8"))).bin[7:]
        if len(department) != 169:
            raise DataIncorrectException("Department form incorrect.")
        department_1 = int(department[   : 64], base=2)
        department_2 = int(department[ 64:128], base=2)
        department_3 = int(department[128:   ], base=2)

        # teacher
        teacher = teacher.strip()

        # time
        time = BitArray(base64.b64decode(time.encode("utf-8"))).bin[5:]
        if len(time) != 91:
            raise DataIncorrectException("Time form incorrect.")
        time_1 = int(time[:64], base=2)
        time_2 = int(time[64:], base=2)
        print(time_1, time_2)

        if id != "":
            courses = CourseObject.query.filter_by(course_id=id)
        else:
            courses = CourseObject.query
            courses = courses.filter(or_(
                CourseObject.department_1.op('&')(department_1),
                CourseObject.department_2.op('&')(department_2),
                CourseObject.department_3.op('&')(department_3),
            ))
            if name != "":
                courses = courses.filter(or_(
                    CourseObject.chinese_name.contains(name),
                    CourseObject.english_name.contains(name),
                ))
            if teacher != "":
                courses = courses.filter(CourseObject.teacher.contains(teacher))
            if precise:
                courses = courses.filter(and_(
                    CourseObject.time_1.op('|')(time_1)==time_1,
                    CourseObject.time_2.op('|')(time_2)==time_2,
                )).params(param_1=time_1, param_2=time_2)
            else:
                courses = courses.filter(or_(
                    CourseObject.time_1.op('&')(time_1),
                    CourseObject.time_2.op('&')(time_2),
                ))
            if place != 0:
                courses = courses.filter(CourseObject.place.op('&')(place))
            print(courses.statement)
            
        if courses != []: courses = courses.all()
        courses = sorted([ c.json for c in courses ], key=lambda c: c["courseId"])
        return HTTPResponse("Success.", data={"amount": len(courses), "courses": courses})

    except PasswordWrongException:
        return HTTPError("Id or password incorrect.", 403)

    except DataIncorrectException as ex:
        return HTTPError(str(ex), 403)

    except Exception as ex:
        # logging
        return HTTPError(str(ex), 404)