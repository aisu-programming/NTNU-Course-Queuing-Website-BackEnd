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
def main_controller():

    robot_logger.info("Main controller thread starts.")

    main_agent_user_id = int(os.environ.get("MAIN_AGENT_USER_ID"))
    main_agent = UserObject.query.filter_by(id=main_agent_user_id).first()
    main_agent = Agent(main_agent.student_id, main_agent.original_password)

    while True:

        if int(datetime.now().strftime("%H")) >= 9:

            db.session.commit()  # Use to refresh session
            orders = OrderObject.query.filter_by(status="activate").all()
            if len(orders) > 0:
                for order in orders:

                    user   = UserObject.query.filter_by(id=order.user_id).first()
                    course = CourseObject.query.filter_by(id=order.course_id).first()
                    robot_logger.info(f"Main agent: Checking vacancy of order from user '{user.student_id}' ({user.name}) of course {course.course_no}.")
                    vacant = main_agent.check_course(course.course_no)

                    if vacant:
                        robot_logger.info(f"Main agent: Order from user '{user.student_id}' ({user.name}) of course {course.course_no} has vacancy!")
                        sub_agent = Agent(user.student_id, user.original_password)
                        robot_logger.info(f"Sub agent '{user.student_id}' ({user.name}): Taking course {course.course_no}!")
                        result = sub_agent.take_course(course.course_no, order.domain)
                        robot_logger.info(f"Sub agent '{user.student_id}' ({user.name}): Result of taking course {course.course_no}: {result}.")

                        if result == "儲存成功":
                            order.update_status("successful")

                    else:
                        # robot_logger.info(f"Main agent: Order from user '{user.student_id}' ({user.name}) of course {course.course_no} has vacancy!")
                        pass
                        
                    time.sleep(SLEEP_TIME)
            
            else:
                time.sleep(SLEEP_TIME)
            
        else:
            time.sleep(SLEEP_TIME)