from fastapi import APIRouter, Depends, Response, status
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.users import UserInCreate, UserInLogin, UserInResponse, UserWithToken
from app.services.authentication import authenticate_user_login
from app.services.jwt import create_access_token_for_user
from app.services.secrets import JWT_SECRET_KEY

router = APIRouter()


@router.post("/signup")
async def signup(
    user_in_create: UserInCreate,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    user = await users_repo.create_user(user_in_create)
    if user:
        return Response(status_code=status.HTTP_201_CREATED, content=user)
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/login")
async def login(
    user_in_login: UserInLogin,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    user = await authenticate_user_login(users_repo, user_in_login)
    if not user:
        raise StarletteHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token_for_user(user, JWT_SECRET_KEY)
    return UserInResponse(
        user=UserWithToken(
            username=user.username,
            email=user.email,
            token=token,
        )
    )
