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


async def authenticate_user_login(users_repo: UsersRepository, user_in_login: UserInLogin) -> Optional[UserInDB]:
    # Validates user_in_login, returns UserInDB if it's valid
    user = await users_repo.get_user_by_username(user_in_login.username)
    if not user:
        return None
    if not security.verify_password(user_in_login.password, user.hashed_password):
        return None
    return user
