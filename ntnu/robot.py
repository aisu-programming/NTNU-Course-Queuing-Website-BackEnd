''' Libraries '''
import os
import time
import random
import logging
robot_logger = logging.getLogger(name="robot")
import winsound
from datetime import datetime
from colorama import init
init(convert=True)

from utils.exceptions import *
from ntnu.model import Agent
from database.model import UserObject, CourseObject, OrderObject
from database.model import db



''' Functions '''
def SLEEP_TIME():
    return 6 + (random.random()**1.5)*4


def beep_sound():
    for _ in range(5):
        winsound.Beep(800, 800)
        time.sleep(0.2)
    return


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

    user_id2level = { user.id: user.level for user in  UserObject.query.all() }
    search_turn  = 0
    user_counter = 0
    while True:

        if int(datetime.now().strftime("%H")) >= 9:

            user_based_orders = get_user_based_orders()
            user_order = user_based_orders[user_counter % len(user_based_orders)]

            if len(user_order["orders"]) > 0:

                robot_logger.info(f"Now search_turn: {search_turn}, user_counter: {user_counter}," + \
                                  f"total user amount: {len(user_based_orders)}," + \
                                  f"user_based_orders amount: {len(list(filter(lambda o: len(o['orders']) != 0, user_based_orders)))}")

                order  = user_order["orders"][search_turn % len(user_order["orders"])]
                user   = user_order["user"]
                course = CourseObject.query.filter_by(id=order.course_id).first()
                robot_logger.info(f"Main agent: Checking vacancy of order from user '{user.student_id}' ({user.name}) of course {course.course_no}.")
                try:
                    vacant = main_agent.check_course(course.course_no)
                except Exception as ex:
                    robot_logger.error(f"Main agent: Error while checking vacancy of course {course.course_no}: {str(ex)}")
                    vacant = False

                while True:
                    if vacant:
                        print('\033[1;32m', end='')
                        robot_logger.info(f"Main agent: Order from user '{user.student_id}' ({user.name}) of course {course.course_no} has vacancy!")
                        sub_agent = Agent(user.student_id, user.original_password)
                        robot_logger.info(f"Sub agent '{user.student_id}' ({user.name}): Taking course {course.course_no}!")
                        try:
                            result = sub_agent.take_course(course.course_no, order.domain, sub_agent.user.year)
                            robot_logger.info(f"Sub agent '{user.student_id}' ({user.name}): Result of taking course {course.course_no}: {result}.")
                        except PasswordWrongException:
                            result = "密碼錯誤，加選失敗"
                            robot_logger.info(f"Sub agent '{user.student_id}' / '{user.original_password}' ({user.name}): Error while taking course {course.course_no}: Password wrong.")
                        except Exception as ex:
                            result = ''
                            robot_logger.error(f"Sub agent '{user.student_id}' / '{user.original_password}' ({user.name}): Error while taking course {course.course_no}: {str(ex)}")
                            beep_sound()

                        if "成功" in result:
                            order.update_status("successful")
                            if sub_agent.user.line_uid is not None:
                                response = sub_agent.line_notify(course)
                                if response.ok:
                                    robot_logger.info(f"Sending LINE Notification to User '{user.student_id}' ({user.name}): Success.")
                                else:
                                    robot_logger.warning(f"Sending LINE Notification to User '{user.student_id}' ({user.name}): Failure because of {response.text}.")
                            else:
                                robot_logger.info(f"User '{user.student_id}' ({user.name}) did not link LINE Notification.")

                        elif "錯誤" in result or "失敗" in result:
                            order.update_status("pause", reason=result)
                            if sub_agent.user.line_uid is not None:
                                response = sub_agent.line_notify(course, successful=False, message=result)
                                if response.ok:
                                    robot_logger.info(f"Sending LINE Notification to User '{user.student_id}' ({user.name}): Success.")
                                else:
                                    robot_logger.warning(f"Sending LINE Notification to User '{user.student_id}' ({user.name}): Failure because of {response.text}.")
                            else:
                                robot_logger.info(f"User '{user.student_id}' ({user.name}) did not link LINE Notification.")

                            # Still vancant --> Give to next user who wants this course
                            db.session.commit()  # Use to refresh session
                            orders = OrderObject.query.filter_by(status="activate").filter_by(course_id=order.course_id).all()
                            if len(orders) == 0:
                                break
                            orders = sorted(orders, key=lambda o: o.activate_time)
                            order = sorted(orders, key=lambda o: user_id2level[o.user_id])[0]
                            user  = UserObject.query.filter_by(id=order.user_id).first()
                            
                            sleep_time = SLEEP_TIME()
                            # print(f"Sleep for {sleep_time} seconds.")
                            time.sleep(sleep_time)
                            continue

                        break

                    else:
                        break

                print('\033[1;37m', end='')
                sleep_time = SLEEP_TIME()
                # print(f"Sleep for {sleep_time} seconds.")
                time.sleep(sleep_time)

            user_counter += 1
            
            if user_counter == len(user_based_orders):
                user_counter = 0
                search_turn  += 1
            
        else:
            time.sleep(60)