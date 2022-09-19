from fastapi import FastAPI, Query, Response
from pydantic import BaseModel

from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone

from db_connection import TblTasks, obj_as_dict, session_scope

app = FastAPI()

page_size = 50


class Task(BaseModel):
    id: Optional[str] = None
    title: str
    content: Optional[str] = None
    deadline: datetime


@app.get("/tasks")
async def get_tasks(page: int = Query(1), title: Optional[str] = Query(None)):
    # page_size = 50

    with session_scope() as session:
        query = session.query(TblTasks).limit(page_size).offset((page - 1) * page_size)
        if title:
            query = query.filter(TblTasks.title.like(f"%{title}%"))

        result = [obj_as_dict(row) for row in query.all()]
        return result


@app.post("/tasks")
async def add_task(task: Task):
    task.id = str(uuid4())
    new_task = TblTasks(
        id=task.id,
        title=task.title,
        content=task.content,
        deadline=task.deadline.astimezone(timezone.utc),
    )  # todo

    with session_scope() as session:
        session.add(new_task)

    return task.dict()


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    with session_scope() as session:
        query = session.query(TblTasks).filter(TblTasks.id == task_id)
        query.delete()

    return Response(status_code=204)
