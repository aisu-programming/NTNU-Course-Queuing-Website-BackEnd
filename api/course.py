''' Libraries '''
import base64
import logging
flask_logger = logging.getLogger(name="flask")
from flask import Blueprint
from bitstring import BitArray
from sqlalchemy import or_, and_

from exceptions import *
from api.auth import login_detect
from api.utils.request import Request
from api.utils.response import *
from api.utils.rate_limit import rate_limit
from database.model import CourseObject



''' Settings '''
__all__ = ["course_api"]
course_api = Blueprint("course_api", __name__)



''' Functions '''
@course_api.route("/", methods=["GET"])
@login_detect
@rate_limit(ip_based=True)
def get_preference(**kwargs):

    def default_preference():
        return HTTPResponse("Success.", data={"sequence": list(range(170))})

    def personal_preference(**kwargs):
        turns = kwargs["user"].user.search_department_turns
        seq = list(zip( list(range(170)), turns ))
        seq = sorted(seq, key=lambda i: i[1], reverse=True)
        return HTTPResponse("Success.", data={"sequence": [ s[0] for s in seq ]})

    try:
        if kwargs.get("user") is None:
            return default_preference()
        else:
            return personal_preference(**kwargs)

    except DataIncorrectException as ex:
        logging.warning(f"DataIncorrectException: {str(ex)}")
        return HTTPError(str(ex), 403)

    except Exception as ex:
        logging.error(f"Unknown exception: {str(ex)}")
        return HTTPError(str(ex), 404)


@course_api.route("/search", methods=["POST"])
@Request.json("course_no: str", "course_name: str", "departments: str", "domains: int",
              "teacher: str", "times: str", "places: int", "precise: bool")
@login_detect
@rate_limit(ip_based=True)
def search_courses(course_no, course_name, departments, domains,
                   teacher, times, places, precise, **kwargs):
    try:

        # If user has logged in
        user = kwargs.get("user")
        if user is not None:
            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) is searching courses.")


        # Check id
        if course_no != "" and len(course_no) != 4:
            raise DataIncorrectException("courseNo form incorrect.")

        # Check name
        course_name = course_name.strip()

        # Check departments
        if departments == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==":
            departments = "Af///////////////////////////w=="
        departments = BitArray(base64.b64decode(departments.encode("utf-8"))).bin[7:]
        if len(departments) != 169:
            raise DataIncorrectException("departments form incorrect.")
        departments_1 = int(departments[   : 64], base=2)
        departments_2 = int(departments[ 64:128], base=2)
        departments_3 = int(departments[128:   ], base=2)

        # Check domains
        # if domains not in list(range(1024)):
        if domains >= 1024 or domains < 0:
            raise DataIncorrectException("domains form incorrect.")

        # Check teacher
        teacher = teacher.strip()

        # Check times
        times = BitArray(base64.b64decode(times.encode("utf-8"))).bin[3:]
        if len(times) != 85:
            raise DataIncorrectException("times form incorrect.")
        times_1 = int(times[:64], base=2)
        times_2 = int(times[64:], base=2)

        # Check places
        if places not in [ 0, 1, 2, 3, 4, 5, 6, 7 ]:
            raise DataIncorrectException("places form incorrect.")


        # Start searching (filtering)
        if course_no != "":
            courses = CourseObject.query.filter_by(course_no=course_no)
        else:
            courses = CourseObject.query
            courses = courses.filter(or_(
                CourseObject.department_1.op('&')(departments_1),
                CourseObject.department_2.op('&')(departments_2),
                CourseObject.department_3.op('&')(departments_3),
            ))
            if course_name != "":
                courses = courses.filter(or_(
                    CourseObject.chinese_name.contains(course_name),
                    CourseObject.english_name.contains(course_name),
                ))
            if teacher != "":
                courses = courses.filter(CourseObject.teacher.contains(teacher))
            if times_1 != 0 or times_2 != 0:
                if precise:
                    courses = courses.filter(and_(
                        CourseObject.time_1.op('|')(times_1)==times_1,
                        CourseObject.time_2.op('|')(times_2)==times_2,
                    )).params(param_1=times_1, param_2=times_2)
                else:
                    courses = courses.filter(or_(
                        CourseObject.time_1.op('&')(times_1),
                        CourseObject.time_2.op('&')(times_2),
                    ))
            if places != 0:
                courses = courses.filter(CourseObject.place.op('&')(places))
            if domains != 0:
                if user is not None:
                    if user.user.year >= 109:
                        courses = courses.filter(CourseObject.domains_109.op('&')(domains))
                    else:
                        courses = courses.filter(CourseObject.domains_106.op('&')(domains))
                else:
                    courses = courses.filter(CourseObject.domains_109.op('&')(domains))

        
        if courses != []: courses = courses.all()
        if user is not None: courses = [ c.json(user.user.year) for c in courses ]
        else               : courses = [ c.json()               for c in courses ]
        courses = sorted(courses, key=lambda c: c["courseNo"])
        for ci in range(len(courses)):
            courses[ci]["isOrdered"] = False


        # If user has logged in
        user = kwargs.get("user")
        if user is not None:
            # Update user's searching preference
            user.user.update_search_department_turns(departments)
            # Filter "isOrdered" key in returning data
            ordered_courses_ids = [ order.course_id for order in user.unfinished_orders ]
            ordered_courses     = CourseObject.query.filter(CourseObject.id.in_(ordered_courses_ids)).all()
            ordered_courses_nos = [ course.course_no for course in ordered_courses ]
            for ci in range(len(courses)):
                if courses[ci]["courseNo"] in ordered_courses_nos:
                    courses[ci]["isOrdered"] = True

        return HTTPResponse("Success.", data={"amount": len(courses), "courses": courses})

    except DataIncorrectException as ex:
        logging.warning(f"DataIncorrectException: {str(ex)}")
        return HTTPError(str(ex), 403)

    except Exception as ex:
        logging.error(f"Unknown exception: {str(ex)}")
        return HTTPError(str(ex), 404)