''' Configurations '''
import os
from dotenv import load_dotenv
load_dotenv(".config/db.env")
load_dotenv(".config/flask.env")
load_dotenv(".config/model.env")
os.environ["ROOT_PATH"] = os.path.dirname(os.path.abspath(__file__))



''' Libraries '''
# Common
import logging
# import threading
from datetime import datetime
# Flask
from flask import Flask
from flask_cors import CORS
from api.auth import auth_api
from api.course import course_api
from database.model import db, CourseObject, import_courses



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Settings '''
logging.basicConfig(filename=f"log/{datetime.now().strftime('%Y.%m.%d-%H.%M')}.log", encoding="utf-8",
                    format="[%(levelname)s] %(asctime)s | %(filename)s: %(funcName)s | %(message)s", level=logging.INFO)
app = Flask(__name__)
# app.config['DEBUG'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.url_map.strict_slashes = False
app.register_blueprint(auth_api, url_prefix="/auth")
app.register_blueprint(course_api, url_prefix="/course")
CORS(app)
db.init_app(app)
with app.app_context():
    db.create_all()
    if db.session.query(CourseObject).count() == 0:
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