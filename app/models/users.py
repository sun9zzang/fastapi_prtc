from pydantic import BaseModel
from sqlalchemy import Column, String

from app.db.db_connection import Base


class User(BaseModel):
    username: str
    password: str
    email: str


class TblUsers(Base):
    __tablename__ = "tbl_users"

    username = Column(String, primary_key=True)
    password = Column(String)
    email = Column(String)
