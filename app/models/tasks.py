from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.db_connection import Base


class TaskBase(BaseModel):
    title: str
    content: str = ""
    deadline: datetime
    username: str


class TaskInCreate(TaskBase):
    ...


class Task(TaskBase):
    id: str


class TaskInUpdate(Task):
    ...


class TblTasks(Base):
    __tablename__ = "tbl_tasks"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, ForeignKey("tbl_users.username"))
    title = Column(String)
    content = Column(Text)
    deadline = Column(DateTime)

    user = relationship("TblUsers", back_populates="tasks")
