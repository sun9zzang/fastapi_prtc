from typing import Optional

from app.db.repositories.users import UsersRepository
from app.models.users import UserInLogin, UserInDB
from app.services import security


async def check_username_is_taken(users_repo: UsersRepository, username: str) -> bool:
    user = await users_repo.get_user_by_username(username)
    if user:
        return True
    else:
        return False


async def check_email_is_taken(users_repo: UsersRepository, email: str) -> bool:
    user = await users_repo.get_user_by_email(email)
    if user:
        return True
    else:
        return False
