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
from flask_cors import CORS
from api.auth import auth_api
from api.order import order_api
from api.course import course_api
from database.model import CourseObject, import_courses
from database.engine import db_session, init_db
# Robot
import threading
from ntnu.robot import main_controller



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Settings '''
from my_logging import *
app = Flask(__name__)
# app.config['DEBUG'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.url_map.strict_slashes = False
app.register_blueprint(auth_api, url_prefix="/auth")
app.register_blueprint(order_api, url_prefix="/order")
app.register_blueprint(course_api, url_prefix="/course")
CORS(app)

# db.init_app(app)
# with app.app_context():
#     db.create_all()

init_db()
if CourseObject.query.count() == 0:
    import_courses()
threading.Thread(target=main_controller, name="Main Controller", daemon=True).start()



''' Functions '''
# def activate_robot():
    # with app.app_context():
        # main_controller()
# threading.Thread(target=activate_robot, name="Main Controller", daemon=True).start()


@app.route("/")
def hello_world():
    return f"<p>Hello world!</p>"


# @app.before_first_request
# def test():
#     from test import main
#     main()
#     return


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    return



''' Run '''
app.run(host="0.0.0.0")