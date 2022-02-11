''' Libraries '''
import base64
import logging
from flask import Blueprint
from bitstring import BitArray
from sqlalchemy import or_, and_

from exceptions import *
# from api.auth import login_required
from api.utils.request import Request
from api.utils.response import *
from database.model import CourseObject  #, OrderObject



''' Settings '''
__all__ = ["course_api"]
course_api = Blueprint("course_api", __name__)



''' Functions '''
@course_api.route("/search", methods=["POST"])
@Request.json("course_no: str", "course_name: str", "department: str",
              "teacher: str", "time: str", "place: int", "precise: bool")
def search_course(course_no, course_name, department, teacher, time, place, precise):
    try:
        # id
        if course_no != "" and len(course_no) != 4:
            raise DataIncorrectException("courseNo form incorrect.")

        # name
        course_name = course_name.strip()

        # department
        department = BitArray(base64.b64decode(department.encode("utf-8"))).bin[7:]
        if len(department) != 169:
            raise DataIncorrectException("department form incorrect.")
        department_1 = int(department[   : 64], base=2)
        department_2 = int(department[ 64:128], base=2)
        department_3 = int(department[128:   ], base=2)

        # teacher
        teacher = teacher.strip()

        # time
        time = BitArray(base64.b64decode(time.encode("utf-8"))).bin[3:]
        if len(time) != 85:
            raise DataIncorrectException("time form incorrect.")
        time_1 = int(time[:64], base=2)
        time_2 = int(time[64:], base=2)
        print(time_1, time_2)

        if course_no != "":
            courses = CourseObject.query.filter_by(course_no=course_no)
        else:
            courses = CourseObject.query
            courses = courses.filter(or_(
                CourseObject.department_1.op('&')(department_1),
                CourseObject.department_2.op('&')(department_2),
                CourseObject.department_3.op('&')(department_3),
            ))
            if course_name != "":
                courses = courses.filter(or_(
                    CourseObject.chinese_name.contains(course_name),
                    CourseObject.english_name.contains(course_name),
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
        courses = sorted([ c.json for c in courses ], key=lambda c: c["courseNo"])
        return HTTPResponse("Success.", data={"amount": len(courses), "courses": courses})

    except DataIncorrectException as ex:
        logging.warning(f"DataIncorrectException: {str(ex)}")
        return HTTPError(str(ex), 403)

    except Exception as ex:
        logging.error(f"Unknown exception: {str(ex)}")
        return HTTPError(str(ex), 404)


# @course_api.route("/order", methods=["POST"])
# @login_required
# @Request.json("course_no: str")
# def order(user, course_no):
#     try:
#         if len(course_no) != 4:
#             raise DataIncorrectException("courseNo form incorrect.")
#         course = CourseObject.query.filter_by(course_no=course_no).first()
#         if course is None:
#             raise DataIncorrectException("courseNo not exist.")
#         else:
#             course = course[0]
#
#         OrderObject(user.user.id, course.id).register()
#         logging.info(f"User '{user.student_id}' ordered for course {course_no}.")
#         return HTTPResponse("Success.")
#
#     except DataIncorrectException as ex:
#         logging.warning(f"DataIncorrectException: {str(ex)}")
#         return HTTPError(str(ex), 403)
#
#     except Exception as ex:
#         logging.error(f"Unknown exception: {str(ex)}")
#         return HTTPError(str(ex), 404)