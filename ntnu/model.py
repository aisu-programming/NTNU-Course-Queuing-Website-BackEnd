''' Libraries '''
import os
import jwt
import json
import requests
from datetime import datetime, timedelta

from database.model import UserObject, CourseObject, OrderObject
from ntnu.utils.webdriver import login_course_taking_system, login_iportal, NTNU_COURSE_QUERY_URL, NTNU_ENROLL_URL
from ntnu.utils.departments import department_str_to_code



''' Parameters '''
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ISSUER = os.environ.get("JWT_ISSUER")
JWT_EXPIRE = timedelta(days=int(os.environ.get("JWT_EXPIRE")))



''' Models '''
class User():
    def __init__(self, student_id, password):
        self.student_id = student_id
        self.password   = password
        self.session    = requests.session()
        self.__search_from_db()

    def __search_from_db(self):
        self.user = UserObject.query.filter_by(student_id=self.student_id).first()
        if self.user is None:
            # User not exist (first time login) --> Register
            # Login failure --> Raise PasswordWrongException
            self.__register()
        else:
            # User exists
            if self.user.original_password == self.password:
                # Password same --> Get orders
                self.orders = OrderObject.query.filter_by(user_id=self.user.id).all()
            else:
                # Update password if it was changed by user via NTNU website
                # Login failure --> Return PasswordWrongException
                self.__update_password()
        return

    def __register(self):
        name, major = self.__set_cookie()
        major = department_str_to_code[major]
        self.user = UserObject(self.student_id, self.password, name, major)
        self.user.register()
        return

    def __update_password(self):
        self.__set_cookie()
        self.user.update_password(self.password)
        return

    # Log into 選課系統 with selenium, get the cookie, and set to session
    def __set_cookie(self):
        cookie, name, major = login_course_taking_system(self.student_id, self.password)
        del cookie["httpOnly"]
        self.session.cookies.set(**cookie)
        self.login_time = datetime.now()
        return name, major

    # Log into 校務行政系統 and get all courses the student has taken
    def __get_course_history(self):
        history = login_iportal(self.student_id, self.password)
        self.history = json.load(history)
        return

    @property
    def jwt(self):
        payload = {
            "iss"   : JWT_ISSUER,
            "exp"   : datetime.utcnow() + JWT_EXPIRE,
            "data"  : { "student_id": self.student_id }
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


class Agent(User):
    def __init__(self, student_id, password):
        super().__init__(student_id, password)

    def __get(self, url, **kwds):
        r = self.session.get(url, **kwds)
        return r

    def __post(self, url, **kwds):
        headers = {"Content-Type": "application/x-www-form-urlencoded", "referer": ''}
        r = self.session.post(url, headers=headers, **kwds)
        return r

    # 切換到「加選」頁面
    def switch_to_add_course_page(self):
        r = self.__get(NTNU_COURSE_QUERY_URL, params={"action": "add"})
        # print("切換到「加選」頁面: " + str(r) + " - " + r.text)

    # 加選課程
    def take_course(self, serial_no, domain):

        # 加選課程前置步驟 1/2
        r = self.post(NTNU_ENROLL_URL, data={
            "action": "checkCourseTime",
            "serial_no": serial_no,
            "direct": "1"
        })
        # print("加選課程前置步驟 1/2: " + str(r) + " - " + r.text)

        # 加選課程前置步驟 2/2
        r = self.post(NTNU_ENROLL_URL, data={
            "action": "checkDomain",
            "serial_no": serial_no,
            "direct": "1"
        })
        # print("加選課程前置步驟 2/2: " + str(r) + " - " + r.text)

        # 如果課程非通識
        if domain == '':
            r = self.post(NTNU_ENROLL_URL, params={
                "action": "add",
                "serial_no": serial_no,
                "direct": "1"
            })
            # print("如果課程非通識: " + str(r) + " - " + r.text)
        # 如果課程是通識
        else:
            r = self.post(NTNU_ENROLL_URL, data={
                "action": "add",
                "serial_no": serial_no,
                "direct": "1",
                "guDomain": domain
            })
            # print("如果課程非通識: " + str(r) + " - " + r.text)

        # 輸出網頁回傳結果內容
        return r.json()