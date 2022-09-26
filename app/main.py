from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Query, Response
from starlette import status

from app.db.db_connection import session_scope
from app.db.repositories.tasks import TasksRepository
from app.models.tasks import Task

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
    if tasks_repository.delete(task_id=task_id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)