''' Libraries '''
from flask import jsonify



''' Settings '''
__all__ = ["HTTPResponse", "HTTPError"]



''' Functions '''
class HTTPBaseResponese(tuple):
    def __new__(cls, resp, status_code=200, cookies={}):
        for c in cookies:
            if cookies[c] == None:
                resp.delete_cookie(c)
            else:
                d = c.split("_httponly")
                resp.set_cookie(d[0], cookies[c], httponly=bool(d[1:]))
        return super().__new__(tuple, (resp, status_code))


class HTTPResponse(HTTPBaseResponese):
    def __new__(cls, message='', status_code=200, status="ok", data=None, cookies={}):
        resp = jsonify({
            "status": status,
            "message": message,
            "data": data,
        })
        return super().__new__(HTTPBaseResponese, resp, status_code, cookies)


class HTTPError(HTTPResponse):
    def __new__(cls, message, status_code, data=None, logout=False):
        cookies = {"jwt": None} if logout else {}
        return super().__new__(HTTPResponse, message, status_code, "err", data, cookies)