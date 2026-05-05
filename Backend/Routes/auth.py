from fastapi import APIRouter
from jose import jwt

router = APIRouter()
SECRET = "SECRET"

@router.post("/login")
def login(user: dict):
    token = jwt.encode(user, SECRET, algorithm="HS256")
    return {"token": token}