from fastapi import FastAPI
from api_user import router as user_router
from api_todo import router as todo_router

app = FastAPI(title="Todo List API")

app.include_router(user_router)
app.include_router(todo_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)