from fastapi import FastAPI, Query
from pydantic import BaseModel
from uuid import uuid4
import pymysql


app = FastAPI()


class Task(BaseModel):
    uid: str | None = None
    title: str
    content: str | None = None
    deadline: str


@app.get("/tasks")
async def get_tasks(page: int = Query(1)):
    PAGE_SIZE = 50
    conn = pymysql.connect(host="localhost", user="root", password="", db="db_task", charset="utf8")
    cur = conn.cursor()
    sql = f"select * from tasks limit {(page - 1) * PAGE_SIZE}, {PAGE_SIZE}"
    cur.execute(sql)

    tasks = []
    if cur:
        col_name = [i[0] for i in cur.description]
        for row in cur:
            json_obj = {}
            for i, col in enumerate(col_name):
                json_obj.update({col: row[i]})
            tasks.append(json_obj)
        
    conn.close()
    return tasks


@app.post("/tasks")
async def add_task(task: Task):
    conn = pymysql.connect(host="localhost", user="root", password="", db="db_task", charset="utf8")
    cur = conn.cursor()
    task.uid = str(uuid4())
    sql = f"insert into tasks values ('{task.uid}', '{task.title}', '{task.content}', '{task.deadline}')"
    cur.execute(sql)
    conn.commit()
    conn.close()
    
    return task


@app.delete("/tasks/{task_uid}")
async def delete_task(task_uid: str):
    conn = pymysql.connect(host="localhost", user="root", password="", db="db_task", charset="utf8")
    cur = conn.cursor()
    sql = f"delete from tasks where uid='{task_uid}'"
    cur.execute(sql)
    conn.commit()
    conn.close()

    return {"task_uid": task_uid}
    