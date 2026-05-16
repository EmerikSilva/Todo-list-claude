from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
import uuid
from api_user import verify_token

router = APIRouter()
DB_FILE = "../db/db.json"

class Todo(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    completed: bool
    user_id: str
    created_at: str

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "todos": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

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
        "created_at": datetime.utcnow().isoformat()
    }
    db["todos"][todo_id] = todo_data
    save_db(db)
    return TodoResponse(**todo_data)

@router.get("/todos", response_model=List[TodoResponse])
def get_todos(current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    return [TodoResponse(**todo) for todo in db["todos"].values() if todo["user_id"] == user_id]

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str, current_user_email: str = Depends(verify_token)):
    db = load_db()
    user_id = next((u["id"] for u in db["users"].values() if u["email"] == current_user_email), None)

    todo = db["todos"].get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return TodoResponse(**todo)

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
        "completed": todo_update.completed
    })
    db["todos"][todo_id] = todo
    save_db(db)
    return TodoResponse(**todo)

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
