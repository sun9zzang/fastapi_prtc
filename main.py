from fastapi import FastAPI, Query
from pydantic import BaseModel
from uuid import uuid4
import pymysql
import sqlalchemy as db


app = FastAPI()

engine = db.create_engine("mysql+pymysql://root:@localhost:3306/db_task")


class Task(BaseModel):
    uid: str | None = None
    title: str
    content: str | None = None
    deadline: str


@app.get("/tasks")
async def get_tasks(page: int = Query(1)):
    PAGE_SIZE = 50
    conn = engine.connect()
    metadata = db.MetaData()
    table_tasks = db.Table('tasks', metadata, autoload=True, autoload_with=engine)

    query = db.select([table_tasks]).limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE)
    result_proxy = conn.execute(query)
    result_set = result_proxy.fetchall()
    
    result_proxy.close()
    conn.close()
    return result_set


@app.post("/tasks")
async def add_task(task: Task):
    conn = engine.connect()
    metadata = db.MetaData()
    table_task = db.Table('tasks', metadata, autoload=True, autoload_with=engine)

    task.uid = str(uuid4())

    query = db.insert(table_task).values(uid=task.uid, title=task.title, content=task.content, deadline=task.deadline)
    result_proxy = conn.execute(query)
    result_proxy.close()
    conn.close()
    
    return task


@app.delete("/tasks/{task_uid}")
async def delete_task(task_uid: str):
    conn = engine.connect()
    metadata = db.MetaData()
    table_task = db.Table('tasks', metadata, autoload=True, autoload_with=engine)

    query = db.delete(table_task).where(table_task.columns.uid == task_uid)
    result_proxy = conn.execute(query)
    result_proxy.close()
    conn.close()

    return {"task_uid": task_uid}
    