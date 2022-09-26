from app.db.repositories.users import UserRepository
from app.models.users import UserInLogin
from app.services import security


async def check_username_is_taken(repo: UserRepository, username: str) -> bool:
    user = await repo.get_user_by_username(username)
    if user:
        return True
    else:
        return False


async def check_email_is_taken(repo: UserRepository, email: str) -> bool:
    user = await repo.get_user_by_email(email)
    if user:
        return True
    else:
        return False


async def authenticate_user(repo: UserRepository, user_in_login: UserInLogin):
    user = await repo.get_user_by_username(user_in_login.username)
    if not user:
        return False
    if not security.verify_password(user_in_login.password, user.hashed_password):
        return False
    return user
