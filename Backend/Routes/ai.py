from fastapi import APIRouter
from ai.smart_prioritizer import prioritize

router = APIRouter()

@router.post("/prioritize")
def prioritize_tasks(data: dict):
    return {"result": prioritize(data["tasks"])}