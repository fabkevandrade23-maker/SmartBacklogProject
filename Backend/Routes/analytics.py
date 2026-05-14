from fastapi import APIRouter, Depends
from routes.auth import get_current_user
from routes.tasks import get_user_tasks
from datetime import datetime
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_summary(user=Depends(get_current_user)):
    tasks  = list(get_user_tasks(user["username"]).values())
    total  = len(tasks)
    done   = sum(1 for t in tasks if t["status"] == "done")
    inprog = sum(1 for t in tasks if t["status"] == "inprogress")
    todo   = sum(1 for t in tasks if t["status"] == "todo")
    return {
        "total":          total,
        "done":           done,
        "inprogress":     inprog,
        "todo":           todo,
        "completion_pct": round(done / total * 100, 1) if total else 0.0,
        "by_priority": {
            "high":   sum(1 for t in tasks if t["priority"] == "high"),
            "medium": sum(1 for t in tasks if t["priority"] == "medium"),
            "low":    sum(1 for t in tasks if t["priority"] == "low"),
        },
        "ai_scored": sum(1 for t in tasks if t.get("ai_score") is not None),
    }

@router.get("/velocity")
def get_velocity(user=Depends(get_current_user)):
    tasks  = list(get_user_tasks(user["username"]).values())
    done   = [t for t in tasks if t["status"] == "done"]
    weekly: dict[str, int] = defaultdict(int)
    for t in done:
        try:
            week = datetime.fromisoformat(t["updated_at"]).strftime("%Y-W%W")
            weekly[week] += 1
        except Exception:
            pass
    avg = round(sum(weekly.values()) / max(len(weekly), 1), 1)
    return {
        "weekly_completions": dict(sorted(weekly.items())),
        "average_per_week":   avg,
        "total_completed":    len(done),
    }

@router.get("/overview")
def get_overview(user=Depends(get_current_user)):
    tasks  = list(get_user_tasks(user["username"]).values())
    total  = len(tasks)
    done   = sum(1 for t in tasks if t["status"] == "done")
    inprog = sum(1 for t in tasks if t["status"] == "inprogress")
    todo   = sum(1 for t in tasks if t["status"] == "todo")

    weekly: dict[str, int] = defaultdict(int)
    for t in [x for x in tasks if x["status"] == "done"]:
        try:
            week = datetime.fromisoformat(t["updated_at"]).strftime("%Y-W%W")
            weekly[week] += 1
        except Exception:
            pass

    by_priority = {}
    for prio in ("high", "medium", "low"):
        subset = [t for t in tasks if t["priority"] == prio]
        d      = sum(1 for t in subset if t["status"] == "done")
        by_priority[prio] = {
            "total": len(subset), "done": d,
            "pct":   round(d / len(subset) * 100, 1) if subset else 0.0,
        }

    recent = sorted(tasks, key=lambda t: t["updated_at"], reverse=True)[:5]

    return {
        "summary": {
            "total": total, "done": done, "inprogress": inprog, "todo": todo,
            "completion_pct": round(done / total * 100, 1) if total else 0.0,
            "ai_scored": sum(1 for t in tasks if t.get("ai_score")),
        },
        "velocity": {
            "weekly_completions": dict(sorted(weekly.items())),
            "average_per_week":   round(sum(weekly.values()) / max(len(weekly), 1), 1),
        },
        "by_priority": by_priority,
        "by_status": {
            "todo":       {"count": todo,   "pct": round(todo   / total * 100, 1) if total else 0},
            "inprogress": {"count": inprog, "pct": round(inprog / total * 100, 1) if total else 0},
            "done":       {"count": done,   "pct": round(done   / total * 100, 1) if total else 0},
        },
        "recent": [{"id": t["id"], "title": t["title"], "status": t["status"],
                    "priority": t["priority"], "updated_at": t["updated_at"]} for t in recent],
    }