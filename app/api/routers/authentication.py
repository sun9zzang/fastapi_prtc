from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.users import UserInCreate, UserInLogin, UserInResponse, UserWithToken
from app.services.authentication import (
    check_username_is_taken,
    check_email_is_taken,
)
from app.services.jwt import create_access_token_for_user
from app.services.secrets import JWT_SECRET_KEY

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


@router.get("/login", response_model=UserInResponse)
async def login(
    user_in_login: UserInLogin,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    login_failed_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="login failed - incorrect login input",
    )

    try:
        user = await users_repo.get_user_by_username(user_in_login.username)
    except Exception as e:  # no user entity
        raise login_failed_error from e

    if not user.check_password(user_in_login.password):
        raise login_failed_error

    token = create_access_token_for_user(user, JWT_SECRET_KEY)

    return UserInResponse(
        user=UserWithToken(
            username=user.username,
            email=user.email,
            token=token,
        )
    )
