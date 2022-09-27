from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime

from app.db.db_connection import Base


class TaskBase(BaseModel):
    title: str
    content: str = ""
    deadline: datetime


class Task(TaskBase):
    id: str


class TaskInCreate(TaskBase):
    ...


class TaskInUpdate(TaskBase):
    ...


class TblTasks(Base):
    __tablename__ = "tbl_tasks"

    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    deadline = Column(DateTime)
