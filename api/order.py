''' Libraries '''
import logging
from flask import Blueprint, request

from exceptions import *
from api.auth import login_required
from api.utils.rate_limit import rate_limit
from api.utils.request import Request
from api.utils.response import *
from database.model import CourseObject, OrderObject



''' Settings '''
__all__ = ["order_api"]
order_api = Blueprint("order_api", __name__)



''' Functions '''
@order_api.route("/", methods=["GET", "PATCH"])
@login_required
@rate_limit
def order(user):

    def get_orders():
        try:
            orders = [ order.json for order in user.orders ]
            return HTTPResponse("Success.", data={"orders": orders})
        except Exception as ex:
            logging.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)

    @Request.json("changes: list")
    def update_orders(changes):
        course_no_before = "courseNo"
        course_no        = "course_no"
        action           = "action"
        STATUS           = [ "activate", "pause" ]
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
            changes = sorted(changes, key=lambda c: c[action], reverse=True)

            # Update
            ACTIVATE = "activate"
            PAUSE    = "pause"
            DELETE   = "delete"
            STATUS   = [ ACTIVATE, PAUSE, DELETE ]
            orders = user.unfinished_orders
            orders_course_ids = [ order.course_id for order in orders ]
            activate_orders_counter = len(list(filter(lambda o: o.status==ACTIVATE, orders)))
            exceed_changes = []
            for change in changes:
                course = CourseObject.query.filter_by(course_no=change[course_no]).first()
                status_target = STATUS[change[action]]

                # OrderObject exist: update it
                if course.id in orders_course_ids:
                    order = orders[orders_course_ids.index(course.id)]
                    status_before = order.status

                    # If status_before == status_target: no need to update
                    if status_before == status_target:
                        pass
                    
                    # Activate the order
                    elif status_target == ACTIVATE:
                        # Hasn't exceed the limitation: permit
                        if activate_orders_counter < user.user.order_limit:
                            logging.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[course_no]} from status '{PAUSE}' to '{ACTIVATE}'.")
                            order.update_status(status_target)
                            activate_orders_counter += 1
                        # Already meet the limitation: refuse to activate the order
                        else:
                            logging.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[course_no]} from status '{PAUSE}' to '{ACTIVATE}' but exceeded the limitation of orders.")
                            exceed_changes.append(change)

                    # Pause the order
                    elif status_target == PAUSE:
                        logging.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[course_no]} from status '{ACTIVATE}' to '{PAUSE}'.")
                        order.update_status(status_target)
                        activate_orders_counter -= 1

                    # Delete the order
                    else:
                        logging.info(f"User '{user.student_id}' ({user.user.name}) deleted order for course {change[course_no]} (status: '{status_before}').")
                        order.cancel()
                        if status_before == ACTIVATE:
                            activate_orders_counter -= 1

                # Order not exist: create new OrderObject
                else:

                    # create new OrderObject with status: ACTIVATE
                    if status_target == ACTIVATE:
                        # Hasn't exceed the limitation: permit
                        if activate_orders_counter < user.user.order_limit:
                            logging.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[course_no]} with status '{ACTIVATE}'.")
                            OrderObject(user.user.id, course.id, ACTIVATE).register()
                            activate_orders_counter += 1
                        # Already meet the limitation: refuse to activate the order
                        else:
                            logging.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[course_no]} with status '{ACTIVATE}' but exceeded the limitation of orders.")
                            exceed_changes.append(change)
                            
                    # create new OrderObject with status: PAUSE
                    elif status_target == PAUSE:
                        logging.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[course_no]} with status '{PAUSE}'.")
                        OrderObject(user.user.id, course.id, PAUSE).register()

            orders = [ order.json for order in user.orders ]
            return HTTPResponse("Success.", data={"orders": orders, "exceedChanges": exceed_changes})

        except DataIncorrectException as ex:
            logging.warning(f"DataIncorrectException: {str(ex)}")
            return HTTPError(str(ex), 403)

        except Exception as ex:
            logging.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)

    methods = { "GET": get_orders, "PATCH": update_orders }
    return methods[request.method]()


@order_api.route("/achievement", methods=["GET"])
@rate_limit(ip_based=True, limit=20)
def get_latest_success_orders():
    try:
        orders = OrderObject.query.filter_by(status="successful").order_by(OrderObject.last_update_time.desc()).limit(10)
        orders = [ order.json_with_user_info for order in orders ]
        return HTTPResponse("Success.", data={"orders": orders})

    except Exception as ex:
        logging.error(f"Unknown exception: {str(ex)}")
        return HTTPError(str(ex), 404)