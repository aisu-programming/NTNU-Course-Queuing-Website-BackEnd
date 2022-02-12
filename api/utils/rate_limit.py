''' Libraries '''
import logging
from flask import request
from functools import wraps
from datetime import datetime

from api.utils.response import HTTPError
from exceptions import BannedException
from database.model import Connection



''' Functions '''
def rate_limit(original_function=None, ip_based=False, limit=3):

    def _decorate(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            try:
                if ip_based:
                    target = request.remote_addr
                else:
                    target = kwargs["user"].student_id

                target_type = ["student_id", "IP"][int(ip_based)]
                conn = Connection.query.filter_by(target=target).first()
                if conn is None:
                    conn = Connection(target, target_type)
                    conn.register()
                else:
                    now = datetime.now()
                    if conn.accept_time is not None and conn.accept_time > now:
                        logging.warning(f"Connection from {target_type}: '{target}' is still under banning. " + \
                                        f"(Banned turn: {conn.banned_turn})")
                        raise BannedException(f"Still under banning.")
                    elif conn.accept_time is not None:
                        logging.warning(f"Connection from {target_type}: '{target}' has been unbanned. " + \
                                        f"(Banned turn: {conn.banned_turn})")
                        conn.unban()
                    else:
                        conn.access()
                        if len(conn.records) > limit:
                            logging.warning(f"DDoS suspicion detected from {target_type}: '{target}'. " + \
                                            f"(Banned turn: {conn.banned_turn} --> {conn.banned_turn+1})")
                            conn.ban()
                            raise BannedException("DDoS suspicion detected.")

                return function(*args, **kwargs)

            except BannedException as ex:
                return HTTPError(str(ex), 403)

            except Exception as ex:
                logging.error(f"Unknown exception: {str(ex)}")
                return HTTPError(str(ex), 404)

        return wrapper

    if original_function:
        return _decorate(original_function)

    return _decorate