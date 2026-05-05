from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def analytics():
    return {
        "todo": 5,
        "progress": 3,
        "done": 7
    }