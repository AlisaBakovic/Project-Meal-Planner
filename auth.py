from datetime import datetime, timedelta
import jwt
from flask import request
from database import SessionLocal
from models import User
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing")

def generate_token(user):

    exp = datetime.utcnow() + timedelta(days=7)

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
        return None

    parts = authorization.split(" ")

    if len(parts) != 2 or parts[0] != "Bearer":
        return None

    token = parts[1]

    payload = decode_token(token)
    user_id = payload["user_id"]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        return None

    return user
