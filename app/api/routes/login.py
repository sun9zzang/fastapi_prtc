from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.users import UserInLogin, UserInResponse, UserWithToken
from app.services.jwt import create_access_token_for_user
from app.services.secrets import JWT_SECRET_KEY

router = APIRouter()


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
