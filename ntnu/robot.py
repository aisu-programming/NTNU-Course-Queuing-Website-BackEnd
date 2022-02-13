''' Libraries '''
import os
import time
import logging
robot_logger = logging.getLogger(name="robot")

from ntnu.model import Agent
from database.model import UserObject, CourseObject, OrderObject


''' Parameters '''
SLEEP_TIME = 30



''' Functions '''
def main_controller():

    robot_logger.info("Main controller thread starts.")

    main_agent_user_id = int(os.environ.get("MAIN_AGENT_USER_ID"))
    main_agent = UserObject.query.filter_by(id=main_agent_user_id).first()
    main_agent = Agent(main_agent.student_id, main_agent.original_password)

    while True:
        orders = OrderObject.query.filter_by(status="activate").all()
        for order in orders:

            user   = UserObject.query.filter_by(id=order.user_id).first()
            course = CourseObject.query.filter_by(id=order.course_id).first()
            robot_logger.info(f"Main agent: Checking vacancy of order from user '{user.student_id}' ({user.name}) of course {course.course_no}.")
            vacant = main_agent.check_course(course.course_no)

            if vacant:
                robot_logger.info(f"Main agent: Order from user '{user.student_id}' ({user.name}) of course {course.course_no} has vacancy!")
                # sub_agent = Agent(user.student_id, user.original_password)
                # sub_agent.take_course(course.course_no)

            else:
                # robot_logger.info(f"Main agent: Order from user '{user.student_id}' ({user.name}) of course {course.course_no} has vacancy!")
                pass
                
        time.sleep(SLEEP_TIME)