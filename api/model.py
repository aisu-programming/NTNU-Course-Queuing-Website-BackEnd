''' Libraries '''
import os
import jwt
import json
import requests
from datetime import datetime, timedelta

from database.model import UserObject
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
            # If login failure --> Raise PasswordWrongException
            self.__register()
        else:
            # User exists
            if self.user.original_password != self.password:
                # Update password if it was changed by user via NTNU website
                # If login failure --> Return PasswordWrongException
                self.__update_password()
        return

    def __register(self):
        _, name, major = login_course_taking_system(self.student_id, self.password)
        major = department_str_to_code[major]
        self.user = UserObject(self.student_id, self.password, name, major)
        self.user.register()
        return

    def __update_password(self):
        login_course_taking_system(self.student_id, self.password)
        self.user.update_password(self.password)
        return

    @property
    def jwt(self):
        payload = {
            "iss"   : JWT_ISSUER,
            "exp"   : datetime.utcnow() + JWT_EXPIRE,
            "data"  : { "student_id": self.student_id }
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")