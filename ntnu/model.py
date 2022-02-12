''' Libraries '''
import os
import jwt
import time
import requests
from datetime import datetime, timedelta

from database.model import UserObject, OrderObject
from ntnu.utils.webdriver import login_course_taking_system, login_iportal, NTNU_WEBSITE_HOST, NTNU_WEBSITE_URL, NTNU_COURSE_QUERY_URL, NTNU_ENROLL_URL
from mapping import department_text2code



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
        name, major = self.__set_cookie()
        major = department_text2code[major]
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
        self.add_course_page = False
        return name, major

    # Log into 校務行政系統 and get all courses the student has taken
    def get_course_history(self):
        history = login_iportal(self.student_id, self.password)
        self.history = history
        return

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        }
        r = self.session.get(url, headers=headers, **kwds)
        return r

    def __post(self, url, extra_headers={}, **kwds):
        headers = {
            "Host": NTNU_WEBSITE_HOST,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept": "*/*",
        }
        for k, v in extra_headers.items(): headers[k] = v
        r = self.session.post(url, headers=headers, **kwds)
        return r

    # 切換到「加選」頁面
    def __switch_to_add_course_page(self):
        r = self.__get(NTNU_COURSE_QUERY_URL, params={"action": "add"})
        # print("切換到「加選」頁面: " + str(r) + " - " + r.text)
        self.add_course_page = True
        return r

    # 加選課程
    def take_course(self, course_no, domain=''):

        if self.session.cookies.get("JESSIONID") is None:
            self.__set_cookie()
        if not self.add_course_page:
            self.__switch_to_add_course_page()

        if not self.add_course_page:
            self.__switch_to_add_course_page()

        # 加選課程前置步驟 1/2
        r = self.__post(NTNU_ENROLL_URL, data={
            "action": "checkCourseTime",
            "serial_no": course_no,
            "direct": "1"
        })
        # print("加選課程前置步驟 1/2: " + str(r) + " - " + r.text)

        # 加選課程前置步驟 2/2
        r = self.__post(NTNU_ENROLL_URL, data={
            "action": "checkDomain",
            "serial_no": course_no,
            "direct": "1"
        })
        # print("加選課程前置步驟 2/2: " + str(r) + " - " + r.text)

        extra_headers = {
            'Host': NTNU_WEBSITE_HOST,
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': NTNU_WEBSITE_URL,
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'{NTNU_COURSE_QUERY_URL}?action=add',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        # 如果課程非通識
        if domain == '':
            r = self.__post(
                NTNU_ENROLL_URL,
                extra_headers=extra_headers,
                params={
                    "action": "add",
                    "serial_no": course_no,
                    "direct": "1"
                })
            # print("如果課程非通識: " + str(r) + " - " + r.text)
        # 如果課程是通識
        else:
            r = self.__post(
                NTNU_ENROLL_URL,
                extra_headers=extra_headers,
                data={
                    "action": "add",
                    "serial_no": course_no,
                    "direct": "1",
                    "guDomain": domain
                })
            # print("如果課程非通識: " + str(r) + " - " + r.text)

        # 輸出網頁回傳結果內容
        return r

    def get_all_ntnu_courses(self):
        if self.session.cookies.get("JESSIONID") is None:
            self.__set_cookie()
        if not self.add_course_page:
            self.__switch_to_add_course_page()
        payload = "limit=999999&page=1&start=0"
        for i in range(3):
            print(f"Send {i+1} time")
            r = self.__post(NTNU_COURSE_QUERY_URL, data=payload)
            if r.text == '': time.sleep(3)
            else           : break
        if r.text == '': return {}
        else           : return r.json()