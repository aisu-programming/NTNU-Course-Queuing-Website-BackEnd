''' Configurations '''
from dotenv import load_dotenv
load_dotenv(".config/db.env")
load_dotenv(".config/flask.env")
load_dotenv(".config/model.env")



''' Libraries '''
import os
from flask import Flask
from flask_cors import CORS
from api.auth import auth_api
from database.model import db



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Settings '''
flask_app = Flask(__name__)
# flask_app.config['DEBUG'] = True
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
# app.url_map.strict_slashes = False
flask_app.register_blueprint(auth_api, url_prefix="/auth")
CORS(flask_app)
db.init_app(flask_app)
with flask_app.app_context():
    db.create_all()



''' Functions '''
@flask_app.route("/")
def hello_world():
    return f"<p>Hello world!</p>"


''' Run '''
flask_app.run(host="0.0.0.0")