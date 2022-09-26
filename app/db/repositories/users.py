from app.db.repositories.base import BaseRepository
from app.models.users import User, UserInCreate, UserInDB, TblUsers


class UserRepository(BaseRepository):
    def get_user_by_username(self, username: str):
        with self.session() as session:
            user_row = (
                session.query(TblUsers).filter(TblUsers.username == username).first()
            )
            if user_row:
                return User(**user_row.__dict__)
            else:
                return None

    def create_user(self, user: UserInCreate):
        user_new = UserInDB(
            username=user.username,
            email=user.email,
            hashed_password=
        )
        user_new_row = TblUsers(**User.__dict__)
        with self.session() as session:
            session.add(user_new_row)
            return user

    def update_user(
        self,
        user: User,
        username: str,
        email: str,
        password: str,
    ):

        with self.session() as session:
            user_row = (
                session.query(TblUsers)
                .filter(TblUsers.username == user.username)
                .first()
            )

            user_row.username = username or user_row.username
            user_row.email = email or user_row.email
            user_row.password = password or user_row.password

            session.update(user_row)
            return User(**user_row.__dict__)
