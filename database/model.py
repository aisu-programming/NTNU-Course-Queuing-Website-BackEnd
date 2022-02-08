''' Libraries '''
import os
import json
from tqdm import tqdm
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, SMALLINT, CHAR, VARCHAR, BINARY, BIT, BOOLEAN, DATETIME

from mapping import department_code2id
from database.utils import AES_encode, AES_decode, process_time_info



''' Models '''
db = SQLAlchemy()


class UserObject(db.Model):
    __tablename__ = 'users'
    id         = Column(TINYINT(unsigned=True), primary_key=True)
    student_id = Column(CHAR(9),     nullable=False, unique=True)
    password   = Column(BINARY(48),  nullable=False)
    name       = Column(VARCHAR(10), nullable=False)
    # grade      = Column(TINYINT(unsigned=True))
    major      = Column(VARCHAR(4),  nullable=False)
    level      = Column(TINYINT,     default=1)
    major_2    = Column(VARCHAR(4))
    minor      = Column(VARCHAR(4))

    def __init__(self, student_id, password, name,
                 major, level=None, major_2=None, minor=None):
        self.student_id = student_id
        self.password   = AES_encode(password)
        self.name       = name
        self.major      = major
        self.level      = level
        self.major_2    = major_2
        self.minor      = minor

    @property
    def original_password(self):
        password = AES_decode(self.password)
        return password

    def register(self):
        db.session.add(self)
        db.session.commit()
        return

    def update_password(self, password):
        self.password = AES_encode(password)
        db.session.commit()
        return


class CourseObject(db.Model):
    __tablename__ = 'courses'
    id           = Column(SMALLINT(unsigned=True), primary_key=True)
    course_id    = Column(CHAR(4),      nullable=False, unique=True)
    course_code  = Column(CHAR(9),      nullable=False)
    chinese_name = Column(VARCHAR(30),  nullable=False)
    english_name = Column(VARCHAR(150), nullable=False)
    credit       = Column(TINYINT,      nullable=False)
    subject      = Column(BINARY(22),   nullable=False)  # 170 / 8 bits = 21.??? bytes
    time_info    = Column(VARCHAR(100), nullable=False)
    time         = Column(BINARY(12),   nullable=False)  # 91 / 8 bits = 11.??? bytes
    place        = Column(BIT(3),       nullable=False)  # 本部, 公館, 其他

    def __init__(
        self, course_id, course_code, chinese_name, english_name, 
        credit, subject, time_info, time, place
    ):
        self.course_id    = course_id
        self.course_code  = course_code
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.credit       = credit
        self.subject      = subject
        self.time_info    = time_info
        self.time         = time
        self.place        = place

    def register(self):
        db.session.add(self)
        db.session.commit()
        return


class OrderObject(db.Model):
    __tablename__ = 'orders'
    id               = Column(TINYINT(unsigned=True), primary_key=True)
    user_id          = Column(TINYINT(unsigned=True), db.ForeignKey('users.id'), nullable=False)
    course_id        = Column(TINYINT(unsigned=True), db.ForeignKey('courses.id'), nullable=False)
    finished         = Column(BOOLEAN, default=False)
    insert_time      = Column(DATETIME, default=datetime.now)
    last_update_time = Column(DATETIME, onupdate=datetime.now, default=datetime.now)

    def __init__(self, user_id, course_id):
        self.user_id   = user_id
        self.course_id = course_id


def import_courses():
    ROOT_PATH = os.environ.get("ROOT_PATH")
    with open(f"{ROOT_PATH}/courses_2022-2.json", encoding="utf-8") as json_file:
        courses = json.load(json_file)["List"]
    for course in tqdm(courses, desc="Importing course", ascii=True):
        course_id    = course["serialNo"]
        course_code  = course["courseCode"]
        chinese_name = course["chnName"]
        english_name = course["engName"]
        credit       = course["credit"]
        subject      = course["deptCode"]
        # teacher      = course["teacher"]
        # limit_count  = course["limitCountH"]
        time_info    = course["timeInfo"]

        credit = int(float(credit))
        subject = department_code2id[subject]
        tmp = [0] * 170
        tmp[subject] = 1
        subject = int(''.join(str(s) for s in tmp), base=2).to_bytes(22, byteorder='big')
        time, place = process_time_info(time_info)
        
        CourseObject(course_id, course_code, chinese_name, english_name, credit, subject, time_info, time, place).register()
        
    return