from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
import pandas as pd


app = FastAPI()


class Task(BaseModel):
    uid: str | None = None
    title: str
    content: str | None = None
    deadline: str


@app.get("/tasks/")
async def get_tasks():
    try:
        current_tasks_df = pd.read_csv("DB_task.csv", index_col=0)
    except pd.errors.EmptyDataError:
        return {"current_task": ""}
    else:
        return {"current_task": current_tasks_df.to_json(orient="records")}


@app.post("/tasks/")
async def add_task(task: Task):
    task.uid = str(uuid4())
    task_df = pd.DataFrame.from_records([{"uid": task.uid, "title": task.title, "content": task.content, "deadline": task.deadline}])
    task_df.to_csv("DB_task.csv", mode="a", header=False, index=False)
    return {"msg": "Task added successfully!", "title_task_added": task.title}


@app.delete("/tasks/{task_uid}")
async def delete_task(task_uid: str):
    current_tasks_df = pd.read_csv("DB_task.csv", index_col=0)
    print(current_tasks_df.to_string())
    current_tasks_df = current_tasks_df.loc[current_tasks_df.index != task_uid]
    current_tasks_df.to_csv("DB_task.csv")
    return {"task_del_message": "Task deleted successfully!", "uid_task_deleted": task_uid}
    