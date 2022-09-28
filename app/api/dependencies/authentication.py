from typing import Callable

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.api.dependencies.database import get_repository
from app.core.config import JWT_SECRET_KEY, JWT_TOKEN_PREFIX
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.models.users import User
from app.services import jwt

HEADER_KEY = "Authorization"


def get_current_user_authorizer() -> Callable:
    return _get_current_user


def _get_authorization_header_retriever() -> Callable:
    return _get_authorization_header


def _get_authorization_header(
    api_key: str = Security(APIKeyHeader(name=HEADER_KEY, auto_error=False)),
) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong token prefix",
        )
    if token_prefix != JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong token prefix",
        )

    return token


def _get_current_user(
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    token: str = Depends(_get_authorization_header_retriever()),
) -> User:
    try:
        username = jwt.get_username_from_token(token, JWT_SECRET_KEY)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="malformed payload"
        )

    try:
        return await users_repo.get_user_by_username(username=username)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="malformed payload"
        )
