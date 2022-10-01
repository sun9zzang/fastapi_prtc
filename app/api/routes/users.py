from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.core import config
from app.db.repositories.users import UsersRepository
from app.models.users import User, UserInResponse, UserWithToken, UserInUpdate
from app.services.authentication import check_username_is_taken, check_email_is_taken
from app.services import jwt

router = APIRouter()


@router.post(
    "",
    response_model=UserInResponse,
    name="users:retrieve-current-user",
    status_code=status.HTTP_200_OK,
)
async def retrieve_current_user(
    current_user: User = Depends(get_current_user_authorizer()),
):

    token = jwt.create_access_token_for_user(current_user, config.JWT_SECRET_KEY)

    return UserInResponse(
        user=UserWithToken(
            username=current_user.username,
            email=current_user.email,
            token=token,
        ),
    )


@router.put(
    "",
    response_model=UserInResponse,
    name="users:update-current-user",
    status_code=status.HTTP_200_OK,
)
async def update_current_user(
    user_in_update: UserInUpdate,
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):

    if user_in_update.username and user_in_update.username != current_user.username:
        if await check_username_is_taken(users_repo, user_in_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username is already taken",
            )

    if user_in_update.email and user_in_update.email != current_user.email:
        if await check_email_is_taken(users_repo, user_in_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email is already taken",
            )

    user_in_db = await users_repo.update_user(
        user=current_user,
        user_in_update=user_in_update,
    )

    token = jwt.create_access_token_for_user(user_in_db, config.JWT_SECRET_KEY)

    return UserInResponse(
        user=UserWithToken(
            username=user_in_db.username,
            email=user_in_db.email,
            token=token,
        )
    )


@router.delete(
    "",
    name="users:withdraw-current-user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def withdraw_current_user(
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    await users_repo.withdraw_user(username=current_user.username)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
