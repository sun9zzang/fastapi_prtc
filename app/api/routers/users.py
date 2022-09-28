from fastapi import APIRouter, Depends

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.core.config import JWT_SECRET_KEY
from app.db.repositories.users import UsersRepository
from app.models.users import User, UserInResponse, UserInUpdate, UserWithToken
from app.services import jwt


router = APIRouter()


@router.get("", response_model=UserInResponse)
async def get_current_user(user: User = Depends(get_current_user_authorizer())):
    token = jwt.create_access_token_for_user(user, JWT_SECRET_KEY)
    return UserInResponse(
        user=UserWithToken(
            **user.dict(),
            token=token,
        )
    )


@router.patch("", response_model=UserInResponse)
async def update_current_user(
    user_in_update: UserInUpdate,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    pass
