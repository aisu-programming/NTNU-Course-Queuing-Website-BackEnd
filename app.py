''' Configurations '''
from dotenv import load_dotenv
load_dotenv(".config/db.env")
load_dotenv(".config/flask.env")
load_dotenv(".config/model.env")



''' Libraries '''
# Common
import os
import logging
import threading
# Flask
from flask import Flask
from flask_cors import CORS
from api.auth import auth_api
from database.model import db
# NTNU
from ntnu.main import get_all_orders



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Settings '''
app = Flask(__name__)
# app.config['DEBUG'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
# app.url_map.strict_slashes = False
app.register_blueprint(auth_api, url_prefix="/auth")
# app.register_blueprint(profile_api, url_prefix="/profile")
# app.register_blueprint(search_api, url_prefix="/search")
CORS(app)
db.init_app(app)
with app.app_context():
    db.create_all()



''' Functions '''
@app.route("/")
def hello_world():
    return f"<p>Hello world!</p>"


@app.before_first_request
def activate_ntnu_course_taking():
    get_all_orders()



''' Run '''
app.run(host="0.0.0.0")