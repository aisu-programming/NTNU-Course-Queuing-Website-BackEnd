''' Libraries '''
import os
import time
import logging

robot_logger = logging.getLogger(name="robot")
from datetime import datetime

from ntnu.model import Agent
from database.model import UserObject, CourseObject, OrderObject
from database.model import db



''' Parameters '''
SLEEP_TIME = 10



''' Functions '''
def get_user_based_orders():
    db.session.commit()  # Use to refresh session
    orders_all    = OrderObject.query.filter_by(status="activate").all()
    course_ids    = list(set([ order.course_id for order in orders_all ]))
    user_id2level = { user.id: user.level for user in  UserObject.query.all() }
    orders_first = [ sorted(
        sorted(
            list(filter(lambda o: o.course_id == cid, orders_all)),
            key=lambda o: o.activate_time
        ),
        key=lambda o: user_id2level[o.user_id], reverse=True
    )[0]
    for cid in course_ids ]
    users  = UserObject.query.all()
    user_based_orders = [{
        "user"  : user,
        "orders": list(filter(lambda o: o.user_id == user.id, orders_first)),
    } for user in users ]
    return user_based_orders


def main_controller():

    robot_logger.info("Main controller thread starts.")

    main_agent_user_id = int(os.environ.get("MAIN_AGENT_USER_ID"))
    main_agent = UserObject.query.filter_by(id=main_agent_user_id).first()
    main_agent = Agent(main_agent.student_id, main_agent.original_password)

    search_turn  = 0
    user_counter = 0
    while True:

        if int(datetime.now().strftime("%H")) >= 9:

            user_based_orders = get_user_based_orders()
            user_order = user_based_orders[user_counter % len(user_based_orders)]
            robot_logger.info(f"Now search_turn: {search_turn}, user_counter: {user_counter % len(user_based_orders)} / {len(user_based_orders)}")

            if len(user_order["orders"]) > 0:

                # robot_logger.info(f"user_order['orders'] = {user_order['orders']}")

                order  = user_order["orders"][search_turn % len(user_order["orders"])]
                user   = user_order["user"]
                course = CourseObject.query.filter_by(id=order.course_id).first()
                robot_logger.info(f"Main agent: Checking vacancy of order from user '{user.student_id}' ({user.name}) of course {course.course_no}.")
                vacant = main_agent.check_course(course.course_no)

                if vacant:
                    robot_logger.info(f"Main agent: Order from user '{user.student_id}' ({user.name}) of course {course.course_no} has vacancy!")
                    sub_agent = Agent(user.student_id, user.original_password)
                    robot_logger.info(f"Sub agent '{user.student_id}' ({user.name}): Taking course {course.course_no}!")
                    result = sub_agent.take_course(course.course_no, order.domain, sub_agent.user.year)
                    robot_logger.info(f"Sub agent '{user.student_id}' ({user.name}): Result of taking course {course.course_no}: {result}.")

                    if "儲存成功" in result:
                        order.update_status("successful")
                        sub_agent.line_notify(course)
                    elif "衝堂" in result or "重複登記" in result or "性別限修" in result or "失敗" in result:
                        order.update_status("pause", reason=result)
                        sub_agent.line_notify(course, successful=False, message=result)

                time.sleep(SLEEP_TIME)

            user_counter += 1
            
            if user_counter == len(user_based_orders):
                user_counter = 0
                search_turn  += 1
            
        else:
            time.sleep(SLEEP_TIME)