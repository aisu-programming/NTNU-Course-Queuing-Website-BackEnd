''' Libraries '''
import os
import sys
import logging
from datetime import datetime



''' Script '''
log_dir = f"logs/{datetime.now().strftime('%Y.%m.%d-%H.%M.%S')}"
os.makedirs("logs", exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

log_format_str = \
    "[%(levelname)-8s] %(name)-20s | %(asctime)s | %(module)-10s: %(funcName)-15s: %(lineno)-3d | %(message)s"
log_formater = logging.Formatter(log_format_str, datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(f"{log_dir}/all.log")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format_str))
logging.basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format=log_format_str,
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

flask_logger = logging.getLogger(name="flask")
flask_file_handler = logging.FileHandler(f"{log_dir}/flask.log")
flask_file_handler.setFormatter(log_formater)
flask_logger.addHandler(flask_file_handler)

robot_logger = logging.getLogger(name="robot")
robot_file_handler = logging.FileHandler(f"{log_dir}/robot.log")
robot_file_handler.setFormatter(log_formater)
robot_logger.addHandler(robot_file_handler)

ip_protector_logger = logging.getLogger(name="ip_protector")
ip_protector_file_handler = logging.FileHandler(f"{log_dir}/ip_protector.log")
ip_protector_file_handler.setFormatter(log_formater)
ip_protector_logger.addHandler(ip_protector_file_handler)

selenium_logger = logging.getLogger(name="seleniumwire.handler")
selenium_logger.setLevel(logging.WARNING)

my_selenium_logger = logging.getLogger(name="selenium-wire")
my_selenium_file_handler = logging.FileHandler(f"{log_dir}/selenium-wire.log")
my_selenium_file_handler.setFormatter(log_formater)
my_selenium_logger.addHandler(my_selenium_file_handler)