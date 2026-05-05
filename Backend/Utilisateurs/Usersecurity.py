from jose import jwt
from datetime import datetime, timedelta

SECRET = "SECRET_KEY"

def create_token(data: dict):
    return jwt.encode(data, SECRET, algorithm="HS256")