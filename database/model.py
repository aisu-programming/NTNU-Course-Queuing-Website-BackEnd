''' Libraries '''
import os
import json
import pytz
from tqdm import tqdm
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import \
    TINYINT, SMALLINT, CHAR, VARCHAR, \
    FLOAT, BINARY, BIT, DATETIME, ENUM, JSON

from mapping import department_code2id, department_code2text, domain_text, domain_code2text
from database.utils import AES_encode, AES_decode, process_time_info



''' Models '''
TZ_TW = pytz.timezone("Asia/Taipei")
db = SQLAlchemy()

class Connection(db.Model):
    __tablename__ = 'connections'
    id          = Column(TINYINT(unsigned=True), primary_key=True)
    target      = Column(VARCHAR(39), nullable=False, unique=True)  # Length of IPv6 = 39
    target_type = Column(ENUM("IP", "student_id"), nullable=False)
    banned_turn = Column(TINYINT, default=0)
    accept_time = Column(DATETIME)
    records     = Column(JSON)

    def __init__(self, target, target_type):
        self.target      = target
        self.target_type = target_type
        self.records     = [ datetime.now().timestamp() ]

    def register(self):
        db.session.add(self)
        db.session.commit()
        return

    def access(self):
        last_second = datetime.now() - timedelta(seconds=1)
        self.records = list(filter(lambda d: d >= last_second.timestamp(), self.records))
        self.records.append(datetime.now().timestamp())
        db.session.commit()
        return

    def ban(self):
        self.records = []
        self.banned_turn += 1
        self.accept_time = datetime.now() + timedelta(hours=1)
        db.session.commit()
        return

    def unban(self):
        self.records.append(datetime.now().timestamp())
        self.accept_time = None
        db.session.commit()
        return


class UserObject(db.Model):
# class UserObject(Base):
    __tablename__ = 'users'
    id                      = Column(TINYINT(unsigned=True), primary_key=True)
    student_id              = Column(CHAR(9),     nullable=False, unique=True)
    password                = Column(BINARY(48),  nullable=False)
    name                    = Column(VARCHAR(10), nullable=False)
    major                   = Column(VARCHAR(4),  nullable=False)
    level                   = Column(TINYINT,     default=1)
    order_limit             = Column(TINYINT,     default=10)  # Activate orders limitation
    major_2                 = Column(VARCHAR(4))
    minor                   = Column(VARCHAR(4))
    # grade                   = Column(TINYINT(unsigned=True))
    line_uid                = Column(VARCHAR(40))  # 33
    search_department_turns = Column(JSON)

    def __init__(self, student_id, password, name,
                 major, level=None, major_2=None, minor=None):
        self.student_id = student_id
        self.password   = AES_encode(password)
        self.name       = name
        self.major      = major
        self.level      = level
        self.major_2    = major_2
        self.minor      = minor

    def register(self):
        self.search_department_turns = [ 0 ] * 170
        self.search_department_turns[department_code2id[self.major] + 1] = 1
        db.session.add(self)
        db.session.commit()
        return

    def update_password(self, password):
        self.password = AES_encode(password)
        db.session.commit()
        return

    def update_line(self, line_uid):
        self.line_uid = line_uid
        db.session.commit()
        return

    def update_search_department_turns(self, departments):
        search_department_turns = [ d for d in self.search_department_turns ]
        if departments == ''.join([ str(d) for d in [ 1 ] * 169 ]):
            search_department_turns[0] += 1
            self.search_department_turns = search_department_turns
        else:
            for di, d in enumerate(departments):
                if int(d):
                    search_department_turns[di+1] += 1
                    self.search_department_turns = search_department_turns
        db.session.commit()
        return

    @property
    def original_password(self):
        password = AES_decode(self.password)
        return password


class CourseObject(db.Model):
    __tablename__ = 'courses'
    id           = Column(SMALLINT(unsigned=True), primary_key=True)
    course_no    = Column(CHAR(4),      nullable=False, unique=True)
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
    # time: 85 bits
    time_1       = Column(BIT(64),      nullable=False)
    time_2       = Column(BIT(21),      nullable=False)
    # place: 3 bits (本部, 公館, 其他)
    place        = Column(BIT(3),       nullable=False)
    teacher      = Column(VARCHAR(50),  nullable=False)
    # domains: 10 bits ("00UG", "01UG", "02UG", "03UG", "04UG", "05UG", "06UG", "07UG", "08UG", "09UG")
    domains      = Column(BIT(10),       nullable=False)

    def __init__(
        self, course_no, course_code, chinese_name, english_name,
        credit, department, department_1, department_2, department_3,
        time_info, time_1, time_2, place, teacher, domains
    ):
        self.course_no    = course_no
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
        self.domains      = domains

    def register(self):
        db.session.add(self)
        db.session.commit()
        return

    @property
    def json(self):
        return {
            "courseNo"   : self.course_no,
            "courseCode" : self.course_code,
            "chineseName": self.chinese_name,
            "credit"     : self.credit,
            "department" : department_code2text[self.department],
            "timeInfo"   : self.time_info,
            "teacher"    : self.teacher,
            "domains"    : self.domains,
        }


class OrderObject(db.Model):
    __tablename__ = 'orders'
    id                = Column(TINYINT(unsigned=True), primary_key=True)
    user_id           = Column(TINYINT(unsigned=True), ForeignKey('users.id'), nullable=False)
    course_id         = Column(SMALLINT(unsigned=True), ForeignKey('courses.id'), nullable=False)
    status            = Column(ENUM("activate", "pause", "successful"), nullable=False)
    domain            = Column(ENUM('', "00UG", "01UG", "02UG", "03UG", "04UG",
                                    "05UG", "06UG", "07UG", "08UG", "09UG"), default='')
    activate_time     = Column(DATETIME)
    last_update_time  = Column(DATETIME, onupdate=datetime.now, default=datetime.now)
    pause_reason      = Column(TINYINT(unsigned=True), default=0)

    def __init__(self, user_id, course_id, status, domain=''):
        self.user_id   = user_id
        self.course_id = course_id
        self.status    = status
        self.domain    = domain

    def register(self):
        if self.status == "activate":
            self.activate_time = datetime.now()
        db.session.add(self)
        db.session.commit()
        return

    def update_status(self, status, reason=None):
        self.status = status
        if status == "activate":
            self.activate_time = datetime.now()
        elif status == "pause":
            if reason is None:
                self.pause_reason = 0
            elif "衝堂" in reason:
                self.pause_reason = 1
            elif "重複登記" in reason:
                self.pause_reason = 2
        db.session.commit()
        return

    def update_domain(self, domain):
        self.domain = domain
        db.session.commit()
        return

    def cancel(self):
        db.session.delete(self)
        db.session.commit()
        return

    @property
    def json(self):
        course = CourseObject.query.filter_by(id=self.course_id).first()
        return {
            "courseNo"   : course.course_no,
            "chineseName": course.chinese_name,
            "credit"     : course.credit,
            "department" : department_code2text[course.department],
            "timeInfo"   : course.time_info,
            "teacher"    : course.teacher,
            "domains"    : course.domains,
            "status"     : self.status,
            "domain"     : domain_code2text[self.domain] if self.domain != '' else '',
            "pauseReason": self.pause_reason,
        }

    # For latest successful orders in index page
    @property
    def json_with_user_info(self):
        user   = UserObject.query.filter_by(id=self.user_id).first()
        course = CourseObject.query.filter_by(id=self.course_id).first()
        return {
            "student_id" : user.student_id,
            "courseNo"   : course.course_no,
            "chineseName": course.chinese_name,
            "succeedTime": self.last_update_time.replace(tzinfo=TZ_TW),
        }


def import_courses():
    ROOT_PATH = os.environ.get("ROOT_PATH")
    with open(f"{ROOT_PATH}/data/courses_2022-2.json", encoding="utf-8") as json_file:
        courses = json.load(json_file)["List"]
        
    for course in tqdm(courses, desc="Importing course", ascii=True):
        course_no    = course["serialNo"]
        course_code  = course["courseCode"]
        chinese_name = course["chnName"]
        english_name = course["engName"]
        credit       = course["credit"]
        dept_code    = course["deptCode"]
        time_info    = course["timeInfo"]
        teacher      = course["teacher"]
        v_chn_name   = course["v_chn_name"]
        # eng_teaching    = course["engTeach"]
        # limit_count     = course["limitCountH"]
        # authorize_count = course["authorizeP"]
        # option_code     = course["optionCode"]  # 必修, 選修, 通識

        credit = float(credit)
        department = [ 0 ] * 169
        department[department_code2id[dept_code]] = 1
        department_1 = int(''.join(str(s) for s in department[   : 64]), base=2)
        department_2 = int(''.join(str(s) for s in department[ 64:128]), base=2)
        department_3 = int(''.join(str(s) for s in department[128:   ]), base=2)
        time_1, time_2, place = process_time_info(time_info)
        domains = [ 0 ] * 10
        for dti, dt in enumerate(domain_text):
            if dt in v_chn_name: domains[dti] = 1
        domains = int(''.join(str(d) for d in domains), base=2)
        
        CourseObject(
            course_no, course_code, chinese_name, english_name, credit,
            dept_code, department_1, department_2, department_3,
            time_info, time_1, time_2, place, teacher, domains
        ).register()
        
    print('')
    return