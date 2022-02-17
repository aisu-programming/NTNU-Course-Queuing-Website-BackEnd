''' Libraries '''
import logging
flask_logger = logging.getLogger(name="flask")
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



''' Parameters '''
COURSE_NO_BEFORE = "courseNo"
COURSE_NO        = "course_no"
ACTION           = "action"
DOMAIN           = "domain"
ACTIVATE         = "activate"
PAUSE            = "pause"
DELETE           = "delete"
STATUS           = [ ACTIVATE, PAUSE, DELETE ]
DOMAINS          = [ '', "00UG", "01UG", "02UG", "03UG", "04UG", "05UG", "06UG", "07UG", "08UG", "09UG" ]



''' Functions '''
def is_domain_invalid(course, domain_target):
    if course.domains == 0 and domain_target == 0:
        return False
    else:
        domain = [ 0 ] * 10
        if domain_target != 0: domain[domain_target-1] = 1
        domain = int(''.join(str(d) for d in domain), base=2)
        if course.domains & domain:
            return False
        else:
            return True


@order_api.route("/", methods=["GET", "PATCH"])
@login_required
@rate_limit
def order(user):

    def get_orders():
        try:
            orders = [ order.json for order in user.orders ]
            return HTTPResponse("Success.", data={"orders": orders})
        except Exception as ex:
            flask_logger.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)

    @Request.json("changes: list")
    def update_orders(changes):
        try:
            # check
            for change in changes:
                if list(change.keys()) != [ COURSE_NO_BEFORE, ACTION, DOMAIN ]:
                    raise DataIncorrectException("data form invalid.")
                change[COURSE_NO] = change[COURSE_NO_BEFORE]
                del change[COURSE_NO_BEFORE]
                if type(change[COURSE_NO]) != str or type(change[ACTION]) != int or type(change[DOMAIN]) != int:
                    raise DataIncorrectException("data contains invalid data type.")
                # action: 0 = ACTIVATE, 1 = PAUSE, 2 = DELETE
                if change[ACTION] not in [ 0, 1, 2 ]:
                    raise DataIncorrectException("data contains invalid action option.")
                if change[DOMAIN] not in [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]:
                    raise DataIncorrectException("data contains invalid domain option.")
                if len(change[COURSE_NO]) != 4:
                    raise DataIncorrectException("data contains courseNo with incorrect form.")
                course = CourseObject.query.filter_by(course_no=change[COURSE_NO]).first()
                if course is None:
                    raise DataIncorrectException("data contains nonexistent courseNo.")
                if is_domain_invalid(course, change[DOMAIN]):
                    raise DataIncorrectException("data contains invalid domain option.")
            courseNos_list = [ change[COURSE_NO] for change in changes ]
            courseNos_set  = set(courseNos_list)
            if len(courseNos_list) != len(courseNos_set):
                raise DataIncorrectException("data contains duplicate courseNo.")
            changes = sorted(changes, key=lambda c: c[ACTION], reverse=True)

            # Update
            orders = user.unfinished_orders
            orders_course_ids = [ order.course_id for order in orders ]
            activate_orders_counter = len(list(filter(lambda o: o.status==ACTIVATE, orders)))
            exceed_changes = []
            for change in changes:
                course = CourseObject.query.filter_by(course_no=change[COURSE_NO]).first()
                status_target = STATUS[change[ACTION]]
                domain_target = DOMAINS[change[DOMAIN]]

                # OrderObject exist: update it
                if course.id in orders_course_ids:
                    order = orders[orders_course_ids.index(course.id)]
                    status_before = order.status

                    # If status_before == status_target: no need to update status
                    if status_before == status_target:
                        # If order.domain == domain_target: no need to update domain
                        if order.domain == domain_target:
                            pass
                        else:
                            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[COURSE_NO]} from domain '{order.domain}' to '{domain_target}'.")
                            order.update_domain(domain_target)
                    
                    # Activate the order
                    elif status_target == ACTIVATE:
                        # Hasn't exceed the limitation: permit
                        if activate_orders_counter < user.user.order_limit:
                            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[COURSE_NO]} from status '{PAUSE}' to '{ACTIVATE}'.")
                            order.update_status(status_target)
                            # If order.domain == domain_target: no need to update domain
                            if order.domain == domain_target:
                                pass
                            else:
                                flask_logger.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[COURSE_NO]} from domain '{order.domain}' to '{domain_target}'.")
                                order.update_domain(domain_target)
                            activate_orders_counter += 1
                        # Already meet the limitation: refuse to activate the order
                        else:
                            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[COURSE_NO]} from status '{PAUSE}' to '{ACTIVATE}' but exceeded the limitation of orders.")
                            exceed_changes.append(change)

                    # Pause the order
                    elif status_target == PAUSE:
                        flask_logger.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[COURSE_NO]} from status '{ACTIVATE}' to '{PAUSE}'.")
                        order.update_status(status_target)
                        # If order.domain == domain_target: no need to update domain
                        if order.domain == domain_target:
                            pass
                        else:
                            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) update order for course {change[COURSE_NO]} from domain '{order.domain}' to '{domain_target}'.")
                            order.update_domain(domain_target)
                        activate_orders_counter -= 1

                    # Delete the order
                    else:
                        flask_logger.info(f"User '{user.student_id}' ({user.user.name}) deleted order for course {change[COURSE_NO]} (status: '{status_before}').")
                        order.cancel()
                        if status_before == ACTIVATE:
                            activate_orders_counter -= 1

                # Order not exist: create new OrderObject
                else:

                    # create new OrderObject with status: ACTIVATE
                    if status_target == ACTIVATE:
                        # Hasn't exceed the limitation: permit
                        if activate_orders_counter < user.user.order_limit:
                            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[COURSE_NO]} with status '{ACTIVATE}'.")
                            OrderObject(user.user.id, course.id, ACTIVATE, domain_target).register()
                            activate_orders_counter += 1
                        # Already meet the limitation: refuse to activate the order
                        else:
                            flask_logger.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[COURSE_NO]} with status '{ACTIVATE}' but exceeded the limitation of orders.")
                            exceed_changes.append(change)
                            
                    # create new OrderObject with status: PAUSE
                    elif status_target == PAUSE:
                        flask_logger.info(f"User '{user.student_id}' ({user.user.name}) ordered course {change[COURSE_NO]} with status '{PAUSE}'.")
                        OrderObject(user.user.id, course.id, PAUSE, domain_target).register()

            orders = [ order.json for order in user.orders ]
            return HTTPResponse("Success.", data={"orders": orders, "exceedChanges": exceed_changes})

        except DataIncorrectException as ex:
            flask_logger.warning(f"DataIncorrectException: {str(ex)}")
            return HTTPError(str(ex), 403)

        except Exception as ex:
            flask_logger.error(f"Unknown exception: {str(ex)}")
            return HTTPError(str(ex), 404)

    methods = { "GET": get_orders, "PATCH": update_orders }
    return methods[request.method]()


@order_api.route("/achievement", methods=["GET"])
# @rate_limit(ip_based=True)
def get_latest_success_orders():
    try:
        orders = OrderObject.query.filter_by(status="successful").order_by(OrderObject.last_update_time.desc()).limit(10)
        orders = [ order.json_with_user_info for order in orders ]
        orders = sorted(orders, key=lambda o: o["succeedTime"], reverse=True)
        return HTTPResponse("Success.", data={"orders": orders})

    except Exception as ex:
        flask_logger.error(f"Unknown exception: {str(ex)}")
        return HTTPError(str(ex), 404)