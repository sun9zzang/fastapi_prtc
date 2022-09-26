from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime

from app.db.db_connection import Base


class Task(BaseModel):
    id: Optional[str] = None
    title: str
    content: Optional[str] = ""
    deadline: datetime


class TblTasks(Base):
    __tablename__ = "tbl_tasks"

    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    deadline = Column(DateTime)
