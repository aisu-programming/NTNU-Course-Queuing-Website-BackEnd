''' Libraries '''
import os
import sys
import logging
from datetime import datetime



''' Script '''
os.makedirs("logs", exist_ok=True)

log_format_str = \
    "[%(levelname)-8s] %(name)-8s | %(asctime)s | %(module)-10s: %(funcName)-15s: %(lineno)-3d | %(message)s"
log_formater = logging.Formatter(log_format_str, datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(
    f"logs/{datetime.now().strftime('%Y.%m.%d-%H.%M')}_all.log")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format_str))
logging.basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format=log_format_str,
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

flask_logger = logging.getLogger(name="flask")
flask_file_handler = logging.FileHandler(
    f"logs/{datetime.now().strftime('%Y.%m.%d-%H.%M')}_flask.log")
flask_file_handler.setFormatter(log_formater)
flask_logger.addHandler(flask_file_handler)

robot_logger = logging.getLogger(name="robot")
robot_file_handler = logging.FileHandler(
    f"logs/{datetime.now().strftime('%Y.%m.%d-%H.%M')}_robot.log")
robot_file_handler.setFormatter(log_formater)
robot_logger.addHandler(flask_file_handler)

selenium_logger = logging.getLogger(name="seleniumwire.handler")
selenium_logger.setLevel(logging.WARNING)