from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json, os
from routes.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

TASKS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'tasks.json')

# ── Persistance ──
def _ensure():
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)

def load_all_tasks() -> dict:
    _ensure()
    if not os.path.exists(TASKS_FILE):
        return {}
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_all_tasks(data: dict):
    _ensure()
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_tasks(username: str) -> dict:
    return load_all_tasks().get(username, {})

def save_user_tasks(username: str, tasks: dict):
    all_tasks = load_all_tasks()
    all_tasks[username] = tasks
    save_all_tasks(all_tasks)

def next_task_id(tasks: dict) -> int:
    if not tasks:
        return 1
    return max(int(k) for k in tasks.keys()) + 1

# ── Modèles ──
class TaskCreate(BaseModel):
    title:       str
    description: Optional[str] = ""
    priority:    Optional[str] = "medium"
    status:      Optional[str] = "todo"
    assignee:    Optional[str] = ""
    due_date:    Optional[str] = ""

class TaskUpdate(BaseModel):
    title:       Optional[str] = None
    description: Optional[str] = None
    priority:    Optional[str] = None
    status:      Optional[str] = None
    assignee:    Optional[str] = None
    due_date:    Optional[str] = None
    ai_score:    Optional[int] = None

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def validate_priority(p):
    if p and p not in ("high", "medium", "low"):
        raise HTTPException(status_code=422, detail="Priorité invalide : high | medium | low")

def validate_status(s):
    if s and s not in ("todo", "inprogress", "done"):
        raise HTTPException(status_code=422, detail="Statut invalide : todo | inprogress | done")

# ── Routes ──
@router.get("")
def get_tasks(status: Optional[str] = None, priority: Optional[str] = None,
              user=Depends(get_current_user)):
    tasks = list(get_user_tasks(user["username"]).values())
    if status:   tasks = [t for t in tasks if t["status"]   == status]
    if priority: tasks = [t for t in tasks if t["priority"] == priority]
    return sorted(tasks, key=lambda x: x["created_at"], reverse=True)

@router.post("", status_code=201)
def create_task(body: TaskCreate, user=Depends(get_current_user)):
    if not body.title.strip():
        raise HTTPException(status_code=422, detail="Le titre est obligatoire.")
    validate_priority(body.priority)
    validate_status(body.status)
    user_tasks = get_user_tasks(user["username"])
    task_id    = next_task_id(user_tasks)
    task = {
        "id":          task_id,
        "title":       body.title.strip(),
        "description": body.description or "",
        "priority":    body.priority,
        "status":      body.status,
        "assignee":    body.assignee or "",
        "due_date":    body.due_date or "",
        "ai_score":    None,
        "created_at":  now_iso(),
        "updated_at":  now_iso(),
        "created_by":  user["username"],
    }
    user_tasks[str(task_id)] = task
    save_user_tasks(user["username"], user_tasks)
    return task

@router.get("/{task_id}")
def get_task(task_id: int, user=Depends(get_current_user)):
    task = get_user_tasks(user["username"]).get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    return task

@router.put("/{task_id}")
def update_task(task_id: int, body: TaskUpdate, user=Depends(get_current_user)):
    user_tasks = get_user_tasks(user["username"])
    task = user_tasks.get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    updates = body.model_dump(exclude_none=True)
    if "priority" in updates: validate_priority(updates["priority"])
    if "status"   in updates: validate_status(updates["status"])
    task.update(updates)
    task["updated_at"] = now_iso()
    save_user_tasks(user["username"], user_tasks)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, user=Depends(get_current_user)):
    user_tasks = get_user_tasks(user["username"])
    if str(task_id) not in user_tasks:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    del user_tasks[str(task_id)]
    save_user_tasks(user["username"], user_tasks)
    return {"detail": f"Tâche {task_id} supprimée."}

@router.patch("/{task_id}/status")
def update_status(task_id: int, status: str, user=Depends(get_current_user)):
    validate_status(status)
    user_tasks = get_user_tasks(user["username"])
    task = user_tasks.get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    task["status"]     = status
    task["updated_at"] = now_iso()
    save_user_tasks(user["username"], user_tasks)
    return task

@router.delete("")
def delete_all_tasks(user=Depends(get_current_user)):
    save_user_tasks(user["username"], {})
    return {"detail": "Toutes vos tâches ont été supprimées."}