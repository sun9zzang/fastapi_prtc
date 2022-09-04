from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4


app = FastAPI()

current_tasks = []


class Task(BaseModel):
    uid: str | None = None
    title: str
    content: str | None = None
    deadline: str


@app.get("/tasks/")
async def get_tasks():
    return {"current_task": current_tasks}


@app.post("/tasks/")
async def add_task(task: Task):
    task.uid = str(uuid4())
    print(task)
    current_tasks.append(task)
    return {"msg": "Task added successfully!", "title_task_added": task.title}


@app.delete("/tasks/{task_uid}")
async def delete_task(task_uid: str):
    for i, task in enumerate(current_tasks):
        if task.uid == task_uid:
            del current_tasks[i]
            return {"task_del_message": "Task deleted successfully!", "uid_task_deleted": task_uid}
    