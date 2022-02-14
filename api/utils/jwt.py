''' Libraries '''
import os
import jwt



''' Parameters '''
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ISSUER = os.environ.get("JWT_ISSUER")



''' Functions '''
def jwt_decode(token, jwt_secret=None, audience=None, jwt_issuer=None):
    if jwt_secret is not None:
        assert audience   is not None
        assert jwt_issuer is not None
    try:
        if jwt_secret is not None:
            json = jwt.decode(token, jwt_secret,
                              audience=audience,
                              issuer=jwt_issuer,
                              algorithms="HS256")
        else:
            json = jwt.decode(token, JWT_SECRET,
                              issuer=JWT_ISSUER,
                              algorithms="HS256")
    except jwt.exceptions.PyJWTError:
        return None
    return json