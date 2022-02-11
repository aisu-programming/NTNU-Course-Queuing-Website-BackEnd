''' Libraries '''
import logging
from flask import Blueprint, request

from exceptions import *
from api.auth import login_required
from api.utils.request import Request
from api.utils.response import *
from database.model import CourseObject, OrderObject



''' Settings '''
__all__ = ["order_api"]
order_api = Blueprint("order_api", __name__)



''' Functions '''
@order_api.route("/", methods=["GET", "PATCH"])
@login_required
def order(user):

    def get_order():
        try:
            orders = [ order.json for order in user.orders ]
            return HTTPResponse("Success.", data={"orders": orders})
        except Exception as ex:
            logging.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)

    @Request.json("changes: list")
    def update_order(changes):
        course_no_before = "courseNo"
        course_no        = "course_no"
        action           = "action"
        status           = [ "activate", "pause" ]
        try:
            # check
            for change in changes:
                if list(change.keys()) != [course_no_before, action]:
                    raise DataIncorrectException("data contains invalid content.")
                change[course_no] = change[course_no_before]
                del change[course_no_before]
                if type(change[course_no]) != str or type(change[action]) != int:
                    raise DataIncorrectException("data contains invalid data type.")
                # action: 0 = activate, 1 = pause, 2 = delete
                if change[action] not in [0, 1, 2]:
                    raise DataIncorrectException("data contains invalid action option.")
                if len(change[course_no]) != 4:
                    raise DataIncorrectException("data contains courseNo with incorrect form.")
                course = CourseObject.query.filter_by(course_no=change[course_no]).first()
                if course is None:
                    raise DataIncorrectException("data contains nonexistent courseNo.")
            courseNos_list = [ change[course_no] for change in changes ]
            courseNos_set  = set(courseNos_list)
            if len(courseNos_list) != len(courseNos_set):
                raise DataIncorrectException("data contains duplicate courseNo.")

            # Update
            status = ["activate", "pause", "success"]
            orders = user.orders
            orders_course_ids = [ order.course_id for order in orders ]
            for change in changes:
                course = CourseObject.query.filter_by(course_no=change[course_no]).first()
                if course.id in orders_course_ids:
                    order = orders[orders_course_ids.index(course.id)]
                    if change[action] in [0, 1]:
                        logging.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[course_no]} to status '{status[change[action]]}'.")
                        order.update_status(status[change[action]])
                    else:
                        logging.info(f"User '{user.student_id}' ({user.user.name}) deleted order for course {change[course_no]}.")
                        order.cancel()
                else:
                    if change[action] in [0, 1]:
                        logging.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[course_no]} with status '{status[change[action]]}'.")
                        OrderObject(user.user.id, course.id, status[change[action]]).register()

            orders = [ order.json for order in user.orders ]
            return HTTPResponse("Success.", data={"orders": orders})

        except DataIncorrectException as ex:
            logging.warning(f"DataIncorrectException: {str(ex)}")
            return HTTPError(str(ex), 403)

        except Exception as ex:
            logging.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)

    methods = { "GET": get_order, "PATCH": update_order }
    return methods[request.method]()