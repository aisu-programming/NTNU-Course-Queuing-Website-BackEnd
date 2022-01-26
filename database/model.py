''' Libraries '''
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR, VARBINARY, BIT, BOOLEAN, DATETIME, LONGBLOB

from database.utils import AES_encode, AES_decode



''' Models '''
db = SQLAlchemy()


class UserObject(db.Model):
    __tablename__ = 'users'
    id         = Column(TINYINT(unsigned=True), primary_key=True)
    student_id = Column(VARCHAR(9),    nullable=False, unique=True)
    password   = Column(VARBINARY(48), nullable=False)
    name       = Column(VARCHAR(10),   nullable=False)
    # grade      = Column(TINYINT(unsigned=True))
    major      = Column(VARCHAR(4),    nullable=False)
    level      = Column(TINYINT,       default=1)
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
    id           = Column(TINYINT(unsigned=True), primary_key=True)
    course_id    = Column(VARCHAR(4),   nullable=False, unique=True)
    course_code  = Column(VARCHAR(9),   nullable=False)
    chinese_name = Column(VARCHAR(30),  nullable=False)
    english_name = Column(VARCHAR(150), nullable=False)
    credit       = Column(TINYINT,      nullable=False)
    subject      = Column(VARCHAR(4),   nullable=False)
    time         = Column(LONGBLOB(91), nullable=False)

    def __init__(
        self, course_id, course_code, chinese_name, english_name, 
        credit, subject, time
    ):
        self.course_id    = course_id
        self.course_code  = course_code
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.credit       = credit
        self.subject      = subject
        self.time         = time


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
    import os, json
    ROOT_PATH = os.environ.get("ROOT_PATH")
    with open(f"{ROOT_PATH}/courses_2022-2.json", encoding="utf-8") as json_file:
        courses = json.load(json_file)["List"]
    for course in courses:
        # course_id   = course["serialNo"]
        # course_code = course["courseCode"]
        # name        = course["chnName"]
        # credit      = int(course["credit"])
        # subject     = course["deptCode"]
        # teacher     = course["teacher"]
        # limit_count = course["limitCountH"]

        time_info = course["timeInfo"]
        if time_info == "◎密集課程":
            time_1, time_2 = by(0), 1
        elif len(time_info.split(',')) == 1:
            time_info = time_info.split(' ')
            weekday = dict(zip(['一', '二', '三', '四', '五', '六'], list(range(6))))[time_info[0]]
            
            
        # CourseObject
    return