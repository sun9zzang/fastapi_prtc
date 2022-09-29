from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.users import UserInCreate
from app.services.authentication import (
    check_username_is_taken,
    check_email_is_taken,
)

router = APIRouter()


@router.post("", name="auth:register")
async def register(
    user: UserInCreate,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    if await check_username_is_taken(users_repo, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="username is already taken"
        )

    if await check_email_is_taken(users_repo, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email is already taken"
        )

    await users_repo.create_user(user)

    return Response(status_code=status.HTTP_201_CREATED)
