from app.db.repositories.base import BaseRepository
from app.models.users import User, TblUsers


class UserRepository(BaseRepository):
    def get_user_by_username(self, username: str):
        with self.session() as session:
            user_row = (
                session.query(TblUsers).filter(TblUsers.username == username).first()
            )
            if user_row:
                return User(**user_row.__dict__)

    def create_user(self, user: User):
        ...
