''' Configurations '''
import os
from dotenv import load_dotenv
load_dotenv(".config/flask.env")
load_dotenv(".config/robot.env")
load_dotenv(".config/database.env")
load_dotenv(".config/validation.env")
os.environ["ROOT_PATH"] = os.path.dirname(os.path.abspath(__file__))



''' Libraries '''
# Flask
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from api.auth import auth_api
from api.line import line_api
from api.order import order_api
from api.course import course_api
from database.model import db
from database.model import CourseObject, import_courses

# Robot
import threading

from ntnu.robot import main_controller



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Settings '''
from utils.my_logging import *
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
# app.config['DEBUG'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.url_map.strict_slashes = False
app.register_blueprint(auth_api, url_prefix="/auth")
app.register_blueprint(line_api, url_prefix="/line")
app.register_blueprint(order_api, url_prefix="/order")
app.register_blueprint(course_api, url_prefix="/course")

db.init_app(app)
with app.app_context():
    db.create_all()
    if CourseObject.query.count() == 0:
        import_courses()



''' Functions '''
def activate_robot():
    with app.app_context():
        main_controller()
threading.Thread(target=activate_robot, name="Main Controller", daemon=True).start()


# @app.route("/")
# @app.route("/search")
# @app.route("/login")
# @app.route("/rushlist/wait")
# def hello_world():
#     return f"<p>修復中... 請耐心等候 QQ...<br/>等修復好了之後還請大家再重選一次課... 真的很對不起... Orz</p>"


# @app.before_first_request
# def test():
#     from test import main
#     main()
#     return



''' Run '''
# app.run()
app.run(ssl_context='adhoc')
# app.run(ssl_context=("cert/cert1.pem", "cert/privkey1.pem"))
# app.run(host="0.0.0.0", ssl_context=("cert/cert1.pem", "cert/privkey1.pem"))
# app.run(host="0.0.0.0", port=4999, ssl_context=("cert/cert1.pem", "cert/privkey1.pem"))