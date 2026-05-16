from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
import uuid
from api_user import verify_token

router = APIRouter()
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "db", "db.json")

class Todo(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    estimated_hours: Optional[float] = None

class TimeLogEntry(BaseModel):
    duration_seconds: float
    note: Optional[str] = None

class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    completed: bool
    user_id: str
    created_at: str
    estimated_hours: Optional[float] = None
    time_logs: List[dict] = []
    total_seconds: float = 0

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "todos": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def build_response(todo: dict) -> TodoResponse:
    logs = todo.get("time_logs", [])
    total = sum(l["duration_seconds"] for l in logs)
    return TodoResponse(
        id=todo["id"],
        title=todo["title"],
        description=todo.get("description"),
        completed=todo["completed"],
        user_id=todo["user_id"],
        created_at=todo["created_at"],
        estimated_hours=todo.get("estimated_hours"),
        time_logs=logs,
        total_seconds=total,
    )

@router.post("/todos", response_model=TodoResponse)
def create_todo(todo: Todo, current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    todo_id = str(uuid.uuid4())
    todo_data = {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "estimated_hours": todo.estimated_hours,
        "time_logs": [],
    }
    db["todos"][todo_id] = todo_data
    save_db(db)
    return build_response(todo_data)

@router.get("/todos", response_model=List[TodoResponse])
def get_todos(current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    return [build_response(t) for t in db["todos"].values() if t["user_id"] == user_id]

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str, current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    todo = db["todos"].get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return build_response(todo)

@router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, todo_update: Todo, current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    todo = db["todos"].get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    todo.update({
        "title": todo_update.title,
        "description": todo_update.description,
        "completed": todo_update.completed,
        "estimated_hours": todo_update.estimated_hours,
    })
    db["todos"][todo_id] = todo
    save_db(db)
    return build_response(todo)

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: str, current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    todo = db["todos"].get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    del db["todos"][todo_id]
    save_db(db)
    return {"message": "Todo deleted successfully"}

@router.post("/todos/{todo_id}/time-log")
def add_time_log(todo_id: str, log: TimeLogEntry, current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    todo = db["todos"].get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if "time_logs" not in todo:
        todo["time_logs"] = []

    todo["time_logs"].append({
        "duration_seconds": log.duration_seconds,
        "note": log.note or "",
        "logged_at": datetime.utcnow().isoformat(),
    })
    db["todos"][todo_id] = todo
    save_db(db)
    total = sum(l["duration_seconds"] for l in todo["time_logs"])
    return {"message": "Time logged", "total_seconds": total}
