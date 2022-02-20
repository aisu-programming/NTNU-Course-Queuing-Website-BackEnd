''' Libraries '''
import os
import jwt
import json
import time
import logging
my_selenium_logger = logging.getLogger(name="selenium-wire")
import requests
from functools import wraps
from datetime import datetime, timedelta

from mapping import department_text2code
from exceptions import RobotStuckException
from database.model import UserObject, OrderObject
from ntnu.utils.webdriver import send_to_ip_protector, login_course_taking_system, login_iportal
from ntnu.utils.webdriver import NTNU_WEBSITE_HOST, NTNU_COURSE_QUERY_URL



''' Parameters '''
JWT_SECRET  = os.environ.get("JWT_SECRET")
JWT_ISSUER  = os.environ.get("JWT_ISSUER")
JWT_EXPIRE  = timedelta(days=int(os.environ.get("JWT_EXPIRE")))

LINE_BEARER = os.environ.get("LINE_BEARER")



''' Models '''
class User():
    def __init__(self, student_id, password):
        self.student_id      = student_id
        self.password        = password
        self.session         = requests.session()
        self.login_time      = None
        self.add_course_page = False
        self.__search_from_db()

    def __search_from_db(self):
        self.user = UserObject.query.filter_by(student_id=self.student_id).first()
        if self.user is None:
            # User not exist (first time login) --> Register
            # If login failure --> Raise PasswordWrongException
            self.__register()
        else:
            # User exists but password incorrect
            if self.user.original_password != self.password:
                # Update password if it was changed by user via NTNU website
                # If login failure --> Raise PasswordWrongException
                self.__update_password()
        return

    def __register(self):
        my_selenium_logger.info(f"User '{self.student_id}' ({self.user.name}) login first time! Registering...")
        name, major = self.set_cookie()
        major = department_text2code[major]
        self.user = UserObject(self.student_id, self.password, name, major)
        self.user.register()
        my_selenium_logger.info(f"User '{self.student_id}' ({self.user.name}) login first time! Registered successfully!")
        return

    def __update_password(self):
        my_selenium_logger.info(f"User '{self.student_id}' ({self.user.name}) login with a different password. Checking update...")
        self.set_cookie()
        self.user.update_password(self.password)
        my_selenium_logger.info(f"User '{self.student_id}' ({self.user.name}) has successfully update new password.")
        return

    # Log into 選課系統 with selenium, get the cookie, and set to session
    def set_cookie(self):
        # cookies, name, major = send_to_ip_protector(self.student_id, self.password)
        cookies, name, major = login_course_taking_system(self.student_id, self.password)
        del cookies["httpOnly"]
        self.session.cookies.set(**cookies)
        self.login_time = datetime.now()
        self.add_course_page = False
        return name, major

    @property
    def jwt(self):
        payload = {
            "iss"   : JWT_ISSUER,
            "exp"   : datetime.utcnow() + JWT_EXPIRE,
            "data"  : { "student_id": self.student_id }
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @property
    def orders(self):
        return OrderObject.query.filter_by(user_id=self.user.id).all()

    @property
    def unfinished_orders(self):
        return OrderObject.query.filter_by(user_id=self.user.id).filter(OrderObject.status!="successful").all()


class Agent(User):
    def __init__(self, student_id, password):
        super().__init__(student_id, password)
        self.add_course_page = False

    def __get(self, url, **kwds):
        headers = {
            "Host": NTNU_WEBSITE_HOST,
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        }
        r = self.session.get(url, headers=headers, **kwds)
        return r

    def __post(self, url, extra_headers={}, **kwds):
        headers = {
            "Host": NTNU_WEBSITE_HOST,
            "Content-Type": "application/x-www-form-urlencoded",
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            # "Accept": "*/*",
        }
        for k, v in extra_headers.items(): headers[k] = v
        r = self.session.post(url, headers=headers, **kwds)
        return r

    # 切換到「查詢課程」頁面
    def __switch_to_query_course_page(self):
        response = self.__get(NTNU_COURSE_QUERY_URL, params={"action": "query"})
        # print("切換到「查詢課程」頁面: " + str(r) + " - " + r.text)
        if response.ok: self.add_course_page = True
        return

    # 切換到「加選」頁面
    def __switch_to_add_course_page(self):
        response = self.__get(NTNU_COURSE_QUERY_URL, params={"action": "add"})
        # print("切換到「加選」頁面: " + str(r) + " - " + r.text)
        if response.ok: self.add_course_page = True
        return

    # 確保已經切換到「加選」頁面
    def __check_add_course_page(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):

            # 超過 20 分鐘: 重置 Session
            if self.login_time is not None and \
               datetime.now() - self.login_time >= timedelta(minutes=19):
                self.session = requests.session()
                my_selenium_logger.info(f"Agent '{self.student_id}' ({self.user.name}) has reset its session.")

            # JESSIONID 為空: 重新登入
            if self.session.cookies.get("JSESSIONID") is None:
                my_selenium_logger.info(f"Agent '{self.student_id}' ({self.user.name}) setting cookies.")
                self.set_cookie()
                if self.session.cookies.get("JSESSIONID") is None:
                    raise RobotStuckException(f"Agent '{self.student_id}' ({self.user.name}) can't login and set cookies succesfully.")

            # 尚未切換到「加選」頁面
            if not self.add_course_page:
                my_selenium_logger.info(f"Agent '{self.student_id}' ({self.user.name}) switching to add course page.")
                self.__switch_to_add_course_page()
                # self.__switch_to_query_course_page()
                if not self.add_course_page:
                    raise RobotStuckException(f"Agent '{self.student_id}' ({self.user.name}) can't switch to add course page succesfully.")
            return function(self, *args, **kwargs)
        return wrapper

    # 查詢課程是否有空位
    @__check_add_course_page
    def check_course(self, course_no):
        for _ in range(3):
            response = self.__post(
                NTNU_COURSE_QUERY_URL,
                data={
                    "action"      : "showGrid",
                    "actionButton": "query",
                    "serialNo"    : course_no,
                    "notFull"     : 1,
                }
            )
            if response.ok and len(response.text) != 0:
                break
            time.sleep(1)
        if not response.ok:
            raise RobotStuckException(f"Function: check_course get a response {response.status_code}.")
        if len(response.text) == 0:
            raise RobotStuckException("Function: check_course can't get normal response.")
        return bool(json.loads(response.text.replace("'", '"'))["Count"])

    # 加選課程
    def take_course(self, course_no, domain, year):
        # return send_to_ip_protector(
        #     self.student_id, self.password, take_course=True,
        #     course_no=course_no, domain=domain, year=year,
        # )
        return login_course_taking_system(
            self.student_id, self.password, take_course=True,
            course_no=course_no, domain=domain, year=year,
        )

    # # 加選課程
    # @__check_add_course_page
    # def take_course(self, course_no, domain=''):
    #     # 加選課程前置步驟 1/2
    #     r = self.__post(NTNU_ENROLL_URL, data={
    #         "action"  : "checkCourseTime",
    #         "serialNo": course_no,
    #         "direct"  : "1"
    #     })
    #     # print("加選課程前置步驟 1/2: " + str(r) + " - " + r.text)
    #
    #     # 加選課程前置步驟 2/2
    #     r = self.__post(NTNU_ENROLL_URL, data={
    #         "action"  : "checkDomain",
    #         "serialNo": course_no,
    #         "direct"  : "1"
    #     })
    #     # print("加選課程前置步驟 2/2: " + str(r) + " - " + r.text)
    #
    #     extra_headers = {
    #         'Host': NTNU_WEBSITE_HOST,
    #         'Connection': 'keep-alive',
    #         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    #         'X-Requested-With': 'XMLHttpRequest',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"Windows"',
    #         'Origin': NTNU_WEBSITE_URL,
    #         'Sec-Fetch-Site': 'same-origin',
    #         'Sec-Fetch-Mode': 'cors',
    #         'Sec-Fetch-Dest': 'empty',
    #         'Referer': f'{NTNU_COURSE_QUERY_URL}?action=add',
    #         'Accept-Encoding': 'gzip, deflate, br',
    #         'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    #     }
    #     # 如果課程非通識
    #     if domain == '':
    #         r = self.__post(
    #             NTNU_ENROLL_URL,
    #             extra_headers=extra_headers,
    #             params={
    #                 "action"  : "add",
    #                 "serialNo": course_no,
    #                 "direct"  : "1",
    #             })
    #         # print("如果課程非通識: " + str(r) + " - " + r.text)
    #     # 如果課程是通識
    #     else:
    #         r = self.__post(
    #             NTNU_ENROLL_URL,
    #             extra_headers=extra_headers,
    #             data={
    #                 "action"  : "add",
    #                 "serialNo": course_no,
    #                 "direct"  : "1",
    #                 "guDomain": domain,
    #             })
    #         # print("如果課程非通識: " + str(r) + " - " + r.text)
    #
    #     # 輸出網頁回傳結果內容
    #     return r

    # 透過 LINE 通知
    def line_notify(self, course, successful=True, message=None):
        if successful:
            message = f"{self.user.name}，恭喜你排到課程: \n" + \
                    f"- 課程序號: {course.course_no}\n" + \
                    f"- 課程名稱: {course.chinese_name}\n" + \
                    f"- 時間地點: {course.time_info}"
        else:
            assert message is not None
            message = f"{self.user.name}，刷課時發生錯誤，因此已暫停該筆選課: \n" + \
                    f"- 課程序號: {course.course_no}\n" + \
                    f"- 課程名稱: {course.chinese_name}\n" + \
                    f"- 時間地點: {course.time_info}\n" + \
                    f"- 錯誤內容: {message}"

        response = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers={
                "Content-Type" : "application/json",
                "Authorization": f"Bearer {LINE_BEARER}"
            },
            data=json.dumps({
                "to"      : self.user.line_uid,
                "messages": [{
                    "type": "text",
                    "text": message
                }]
            })
        )
        return response

    # # 獲取學校所有課程
    # def get_all_ntnu_courses(self):
    #     if self.session.cookies.get("JESSIONID") is None:
    #         self.set_cookie()
    #     if not self.add_course_page:
    #         self.__switch_to_add_course_page()
    #     payload = "action=showGrid&actionButton=query"
    #     for i in range(3):
    #         print(f"Send {i+1} time")
    #         r = self.__post(NTNU_COURSE_QUERY_URL, data=payload)
    #         if r.text == '': time.sleep(3)
    #         else           : break
    #     if r.text == '': return {}
    #     else           : return r.text