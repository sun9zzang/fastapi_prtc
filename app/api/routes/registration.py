from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.users import UserInCreate
from app.services.authentication import (
    check_username_is_taken,
    check_email_is_taken,
)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_in_create: UserInCreate,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    if await check_username_is_taken(users_repo, user_in_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="username is taken"
        )

    if await check_email_is_taken(users_repo, user_in_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email is taken"
        )

    user = await users_repo.create_user(user_in_create)

    return user
