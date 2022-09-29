from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.db_connection import Base
from app.services import security


class User(BaseModel):
    username: str
    email: str


class UserInLogin(BaseModel):
    username: str
    password: str


class UserInCreate(User):
    password: str


class UserInUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserWithToken(User):
    token: str


class UserInResponse(BaseModel):
    user: UserWithToken


class UserInDB(User):
    salt: str = ""
    hashed_password: str = ""

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)


class TblUsers(Base):
    __tablename__ = "tbl_users"

    username = Column(String, primary_key=True, index=True)
    email = Column(String)
    hashed_password = Column(String)

    tasks = relationship("TblTasks", back_populates="user")
