from typing import Optional

from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist
from app.models.users import User, UserInCreate, UserInDB, TblUsers


class UsersRepository(BaseRepository):
    async def get_user_by_username(self, username: str) -> UserInDB:
        with self.session() as session:
            user_row = (
                session.query(TblUsers).filter(TblUsers.username == username).first()
            )
            if user_row:
                return UserInDB(**user_row.__dict__)
            raise EntityDoesNotExist(
                f"user with username {username} does not exist",
            )

    async def get_user_by_email(self, email: str) -> UserInDB:
        with self.session() as session:
            user_row = session.query(TblUsers).filter(TblUsers.email == email).first()
            if user_row:
                return UserInDB(**user_row.__dict__)
            raise EntityDoesNotExist(
                f"user with email {email} does not exist",
            )

    async def create_user(self, user_in_create: UserInCreate) -> UserInDB:
        user_in_db = UserInDB(
            username=user_in_create.username,
            email=user_in_create.email,
        )
        user_in_db.change_password(user_in_create.password)

        user_row = TblUsers(**user_in_db.dict())
        with self.session() as session:
            session.add(user_row)

        return user_in_db

    async def update_user(
        self,
        user: User,
        username: str,
        email: str,
        password: str,
    ) -> UserInDB:

        with self.session() as session:
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
