from sqlalchemy import Column, String, DateTime, create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

from fastapi import FastAPI, Query, Response
from pydantic import BaseModel

from contextlib import contextmanager
from typing import Optional
from uuid import uuid4
from datetime import datetime


app = FastAPI()

Base = declarative_base()
engine = create_engine("mysql+pymysql://root:@localhost:3306/todo_list", echo=True, future=True)
Session = sessionmaker(bind=engine)


class TblTasks(Base):
    __tablename__ = "tbl_tasks"

    uid = Column(String, primary_key=True)
    title = Column(String)
    content = Column(String)
    deadline = Column(DateTime)

    def __repr__(self):
        return f"TblTasks(uid={self.uid}, title={self.title}, content={self.content}, deadline={self.deadline})"


class Task(BaseModel):
    uid: Optional[str] = None
    title: str
    content: Optional[str] = None
    deadline: datetime


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def obj_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


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
