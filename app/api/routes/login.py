from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.dependencies.database import get_repository
from app.core import config
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.models.users import UserInLogin, UserInResponse, UserWithToken
from app.services.jwt import create_access_token_for_user

router = APIRouter()


@router.post(
    "",
    response_model=UserInResponse,
    name="auth:login",
    status_code=status.HTTP_200_OK,
)
async def login(
    user: UserInLogin = Body(..., embed=True),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    login_failed_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="login failed - incorrect login input",
    )

    try:
        user_in_db = await users_repo.get_user_by_username(user.username)
    except EntityDoesNotExist as existence_error:
        raise login_failed_error from existence_error

    if not user_in_db.check_password(user.password):
        raise login_failed_error

    token = create_access_token_for_user(user_in_db, config.JWT_SECRET_KEY)

    return UserInResponse(
        user=UserWithToken(
            username=user_in_db.username,
            email=user_in_db.email,
            token=token,
        )
    )
