from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist


async def check_username_is_taken(users_repo: UsersRepository, username: str) -> bool:
    try:
        await users_repo.get_user_by_username(username)
    except EntityDoesNotExist:
        return False
    else:
        return True


async def check_email_is_taken(users_repo: UsersRepository, email: str) -> bool:
    try:
        await users_repo.get_user_by_email(email)
    except EntityDoesNotExist:
        return False
    else:
        return True
