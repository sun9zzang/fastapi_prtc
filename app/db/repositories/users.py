from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist
from app.db.db_connection import get_scoped_session
from app.models.users import User, UserInCreate, UserInDB, TblUsers

import logging


# noinspection PyMethodMayBeStatic
class UsersRepository(BaseRepository):
    async def get_user_by_username(self, username: str) -> UserInDB:
        with get_scoped_session() as session:
            user_row = (
                session.query(TblUsers).filter(TblUsers.username == username).first()
            )
            if user_row:
                return UserInDB(**user_row.__dict__)
            raise EntityDoesNotExist(
                f"user with username {username} does not exist",
            )

    async def get_user_by_email(self, email: str) -> UserInDB:
        with get_scoped_session() as session:
            user_row = session.query(TblUsers).filter(TblUsers.email == email).first()
            if user_row:
                return UserInDB(**user_row.__dict__)
            raise EntityDoesNotExist(
                f"user with email {email} does not exist",
            )

    async def create_user(self, *, user: UserInCreate) -> UserInDB:
        user_in_db = UserInDB(
            username=user.username,
            email=user.email,
        )
        user_in_db.change_password(user.password)

        user_row = TblUsers(**user_in_db.dict())
        with get_scoped_session() as session:
            session.add(user_row)

        return user_in_db

    async def update_user(
        self,
        *,
        user: User,
        username: str,
        email: str,
        password: str,
    ) -> UserInDB:

        with get_scoped_session() as session:
            user_row = session.query(TblUsers).filter(
                TblUsers.username == user.username
            )

            user_in_db = await self.get_user_by_username(user.username)

            user_in_db.username = username or user_row.username
            user_in_db.email = email or user_row.email
            if password:
                user_in_db.change_password(password)

            user_row.update(user_in_db.dict(), synchronize_session="fetch")
            return user_in_db

    async def withdraw_user(self, *, username: str) -> None:
        with get_scoped_session() as session:
            user_row = (
                session.query(TblUsers).filter(TblUsers.username == username).first()
            )
            if user_row is not None:
                session.delete(user_row)
            raise EntityDoesNotExist(
                f"user with username {username} does not exist",
            )
