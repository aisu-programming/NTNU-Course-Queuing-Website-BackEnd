''' Configurations '''
import os
from dotenv import load_dotenv
load_dotenv(".config/db.env")
load_dotenv(".config/flask.env")
load_dotenv(".config/model.env")
os.environ["ROOT_PATH"] = os.path.dirname(os.path.abspath(__file__))



''' Libraries '''
# Common
import sys
import logging
# import threading
from datetime import datetime
# Flask
from flask import Flask
from flask_cors import CORS
from api.auth import auth_api
from api.order import order_api
from api.course import course_api
from database.model import db, CourseObject, import_courses



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Logging '''
os.makedirs("logs", exist_ok=True)
logging_format = "[%(levelname)-8s] %(name)-8s | %(asctime)s | %(module)-10s: %(funcName)-10s: %(lineno)-3d | %(message)s"
logging.basicConfig(filename=f"logs/{datetime.now().strftime('%Y.%m.%d-%H.%M')}.log", datefmt="%Y-%m-%d %H:%M:%S",
                    format=logging_format, level=logging.INFO)
console_logger = logging.StreamHandler(sys.stdout)
console_logger.setFormatter(logging.Formatter(logging_format))
logging.getLogger().addHandler(console_logger)
selenium_logger = logging.getLogger(name="seleniumwire.handler")
selenium_logger.setLevel(logging.WARNING)



''' Settings '''
app = Flask(__name__)
# app.config['DEBUG'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.url_map.strict_slashes = False
app.register_blueprint(auth_api, url_prefix="/auth")
app.register_blueprint(order_api, url_prefix="/order")
app.register_blueprint(course_api, url_prefix="/course")
CORS(app)
db.init_app(app)
with app.app_context():
    db.create_all()
    if CourseObject.query.count() == 0:
        import_courses()



''' Functions '''
@app.route("/")
def hello_world():
    return f"<p>Hello world!</p>"


# @app.before_first_request
# def activate_ntnu_course_taking():
#     pass


@app.before_first_request
def test():
    from test import main
    main()
    return



''' Run '''
app.run(host="0.0.0.0")