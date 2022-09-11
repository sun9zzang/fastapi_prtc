from fastapi import FastAPI, Query, Response
from pydantic import BaseModel

from typing import Optional
from uuid import uuid4
from datetime import datetime

from db_connection import TblTasks, obj_as_dict, session_scope


app = FastAPI()


class Task(BaseModel):
    uid: Optional[str] = None
    title: str
    content: Optional[str] = None
    deadline: datetime


@app.get("/tasks")
async def get_tasks(page: int = Query(1), title: Optional[str] = Query(None)):
    page_size = 50
    # print(f"page: {page}, title: {title}")

    with session_scope() as session:
        if title:
            query = session.query(TblTasks).filter(TblTasks.title.like(f"%{title}%")).limit(page_size).offset(
                (page - 1) * page_size)
        else:
            query = session.query(TblTasks).limit(page_size).offset((page - 1) * page_size)

        result = [obj_as_dict(row) for row in query.all()]
        return result


@app.post("/tasks")
async def add_task(task: Task):
    task.uid = str(uuid4())
    new_task = TblTasks(uid=task.uid, title=task.title, content=task.content, deadline=task.deadline)

    with session_scope() as session:
        session.add(new_task)

    return task.dict()


@app.delete("/tasks/{task_uid}")
async def delete_task(task_uid: str):
    with session_scope() as session:
        query = session.query(TblTasks).filter(TblTasks.uid == task_uid)
        query.delete()

    return Response(status_code=204)
