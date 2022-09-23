from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Query

from app.db.db_connection import session_scope
from app.db.repositories.tasks import TasksRepository
from app.models import Task

app = FastAPI()


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
    return tasks_repository.delete(task_id=task_id)
