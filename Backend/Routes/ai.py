from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ai.smart_prioritizer import prioritize
from routes.auth import get_current_user
from routes.tasks import get_user_tasks
import os

router = APIRouter(prefix="/ai", tags=["AI"])

class PrioritizeRequest(BaseModel):
    tasks:    list | str
    context:  Optional[str] = ""
    criteria: Optional[str] = "impact"

class AutoPrioritizeRequest(BaseModel):
    context:  Optional[str] = ""
    criteria: Optional[str] = "impact"

@router.post("/prioritize")
def prioritize_tasks(req: PrioritizeRequest, user=Depends(get_current_user)):
    """Priorise une liste de tâches fournie manuellement."""
    try:
        result = prioritize(req.tasks, req.context, req.criteria)
        return {"result": result, "model": "gpt-4o"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prioritize/auto")
def auto_prioritize(req: AutoPrioritizeRequest, user=Depends(get_current_user)):
    """Récupère toutes les tâches du backlog et les priorise automatiquement."""
    tasks = list(get_user_tasks(user["username"]).values())
    if not tasks:
        raise HTTPException(status_code=400, detail="Aucune tâche dans le backlog")

    tasks_str = "\n".join(
        f"{i+1}. [{t['priority'].upper()}] {t['title']} — {t['description'] or 'sans description'}"
        for i, t in enumerate(tasks)
    )
    try:
        result = prioritize(tasks_str, req.context, req.criteria)
        for i, task in enumerate(tasks):
            task["ai_score"] = len(tasks) - i
        return {"result": result, "model": "gpt-4o", "tasks_count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def ai_status(user=Depends(get_current_user)):
    """Vérifie si la clé OpenAI est configurée."""
    key = os.getenv("OPENAI_API_KEY", "")
    return {"configured": bool(key and key.startswith("sk-")), "model": "gpt-4o"}