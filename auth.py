from datetime import datetime, timedelta
import jwt
from flask import request

SECRET_KEY = "supersecretkey"

def generate_token(user):

    exp = datetime.utcnow() + timedelta(hours=1)

    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": exp
    }


    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token

def decode_token(token):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError ("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError ("Invalid token")

def get_current_user(user):


    try:
        authorization = request.headers.get("Authorization")
        try:
            parts = authorization.split(" ")
            return parts
        except:
            raise ValueError("Invalid token error")

        return authorization
    except:
        raise ValueError ("Missing token")


