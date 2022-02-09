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
# Flask
from flask import Flask
from flask_cors import CORS
from api.auth import auth_api
from api.search import search_api
from database.model import db, CourseObject, import_courses



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Settings '''
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
app = Flask(__name__)
# app.config['DEBUG'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
# app.url_map.strict_slashes = False
app.register_blueprint(auth_api, url_prefix="/auth")
app.register_blueprint(search_api, url_prefix="/search")
# app.register_blueprint(profile_api, url_prefix="/profile")
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