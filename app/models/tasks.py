from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core import config
from app.db.db_connection import Base
from app.services import utils


class TaskBase(BaseModel):
    title: str
    content: str
    deadline: str


class TaskInCreate(TaskBase):
    ...


class Task(TaskBase):
    id: str
    username: str


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

    def convert_to_task(self) -> Task:
        return Task(
            id=self.id,
            username=self.username,
            title=self.title,
            content=self.content,
            deadline=utils.convert_datetime_to_string(self.deadline),
        )
