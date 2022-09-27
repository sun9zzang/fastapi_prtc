from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi import FastAPI, Query, Response, HTTPException
from starlette import status

from app.db.db_connection import session_scope
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UserRepository
from app.models.tasks import Task
from app.models.users import UserInLogin, UserInCreate
from app.services.authentication import authenticate_user

app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.get("/tasks")
async def get_tasks(page_offset: int = Query(1), title: Optional[str] = Query(None)):
    tasks_repository = TasksRepository(session_scope)
    return tasks_repository.get(page_offset=page_offset, title=title)


@app.post("/tasks")
async def add_task(task: Task):
    task.id = str(uuid4())
    tasks_repository = TasksRepository(session_scope)
    return tasks_repository.add(task=task)


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    tasks_repository = TasksRepository(session_scope)
    if tasks_repository.delete(task_id=task_id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/register")
async def register_account(user_in_create: UserInCreate):
    user_repository = UserRepository(session_scope)
    return user_repository.create_user(user_in_create)


@app.get("/login")
async def login(user_in_login: UserInLogin):
    user_repository = UserRepository(session_scope)

    user = authenticate_user(user_repository, user_in_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

