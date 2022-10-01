from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.users import User, UserInCreate
from app.services.authentication import (
    check_username_is_taken,
    check_email_is_taken,
)

router = APIRouter()


@router.post(
    "",
    name="auth:register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserInCreate = Body(..., embed=True),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    if await check_username_is_taken(users_repo, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username is already taken",
        )

    if await check_email_is_taken(users_repo, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email is already taken",
        )

    user_in_db = await users_repo.create_user(user=user)

    return User(
        username=user_in_db.username,
        email=user_in_db.email,
    )
