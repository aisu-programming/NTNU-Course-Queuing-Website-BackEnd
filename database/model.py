''' Libraries '''
import os
import json
from tqdm import tqdm
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import \
    TINYINT, SMALLINT, CHAR, VARCHAR, \
    FLOAT, BINARY, BIT, BOOLEAN, DATETIME

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
    course_code  = Column(CHAR(7),      nullable=False)
    chinese_name = Column(VARCHAR(80),  nullable=False)
    english_name = Column(VARCHAR(120), nullable=False)
    credit       = Column(FLOAT,        nullable=False)
    # department: 169 bits
    department   = Column(CHAR(4),      nullable=False)
    department_1 = Column(BIT(64),      nullable=False) 
    department_2 = Column(BIT(64),      nullable=False)
    department_3 = Column(BIT(41),      nullable=False)
    time_info    = Column(VARCHAR(150), nullable=False)
    # time: 91 bits
    time_1       = Column(BIT(64),      nullable=False)
    time_2       = Column(BIT(27),      nullable=False)
    # place: 3 bits (本部, 公館, 其他)
    place        = Column(BIT(3),       nullable=False)
    teacher      = Column(VARCHAR(30),  nullable=False)

    def __init__(
        self, course_id, course_code, chinese_name, english_name,
        credit, department, department_1, department_2, department_3,
        time_info, time_1, time_2, place, teacher
    ):
        self.course_id    = course_id
        self.course_code  = course_code
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.credit       = credit
        self.department   = department
        self.department_1 = department_1
        self.department_2 = department_2
        self.department_3 = department_3
        self.time_info    = time_info
        self.time_1       = time_1
        self.time_2       = time_2
        self.place        = place
        self.teacher      = teacher

    def register(self):
        db.session.add(self)
        db.session.commit()
        return

    @property
    def json(self):
        return {
            "courseId"   : self.course_id,
            "courseCode" : self.course_code,
            "chineseName": self.chinese_name,
            "englishName": self.english_name,
            "credit"     : self.credit,
            "department" : self.department,
            "timeInfo"   : self.time_info,
            "teacher"    : self.teacher,
        }


class OrderObject(db.Model):
    __tablename__ = 'orders'
    id               = Column(TINYINT(unsigned=True), primary_key=True)
    user_id          = Column(TINYINT(unsigned=True), db.ForeignKey('users.id'), nullable=False)
    course_id        = Column(SMALLINT(unsigned=True), db.ForeignKey('courses.id'), nullable=False)
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
        
    for ei, course in tqdm(enumerate(courses), desc="Importing course", ascii=True):
        course_id    = course["serialNo"]
        course_code  = course["courseCode"]
        chinese_name = course["chnName"]
        english_name = course["engName"]
        credit       = course["credit"]
        department   = course["deptCode"]
        time_info    = course["timeInfo"]
        teacher      = course["teacher"]
        # eng_teaching    = course["engTeach"]
        # limit_count     = course["limitCountH"]
        # authorize_count = course["authorizeP"]
        # option_code     = course["optionCode"]  # 必修, 選修, 通識

        credit = float(credit)
        tmp = [0] * 169
        tmp[department_code2id[department]] = 1
        department_1 = int(''.join(str(s) for s in tmp[   : 64]), base=2)
        department_2 = int(''.join(str(s) for s in tmp[ 64:128]), base=2)
        department_3 = int(''.join(str(s) for s in tmp[128:   ]), base=2)
        time_1, time_2, place = process_time_info(time_info)
        
        course = CourseObject(course_id, course_code, chinese_name, english_name, credit, department, department_1, department_2, department_3, time_info, time_1, time_2, place, teacher)
        course.register()
        
    print('')
    return