''' Libraries '''
import os
import jwt



''' Parameters '''
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ISSUER = os.environ.get("JWT_ISSUER")



''' Functions '''
def jwt_decode(token):
    try:
        json = jwt.decode(token, JWT_SECRET,
                          issuer=JWT_ISSUER, algorithms="HS256")
    except jwt.exceptions.PyJWTError:
        return None
    return json