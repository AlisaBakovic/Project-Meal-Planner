from datetime import datetime, timedelta
import jwt
from flask import request

from database import SessionLocal
from models import User

SECRET_KEY = "supersecretkey"


def generate_token(user):

    exp = datetime.utcnow() + timedelta(hours=1)

    payload = {"user_id": user.id, "role": user.role, "exp": exp}

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def decode_token(token):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def get_current_user():

    authorization = request.headers.get("Authorization")

    if not authorization:
        raise ValueError("Missing token")

    parts = authorization.split(" ")

    if len(parts) != 2 or parts[0] != "Bearer":
        raise ValueError("Invalid token format")

    token = parts[1]

    payload = decode_token(token)
    user_id = payload["user_id"]

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()

    if not user:
        raise ValueError("User not found")

    return user
