import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.db.repositories.users import UsersRepository
from app.db.db_connection import get_scoped_session


async def test_user_can_registration(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    username = "username"
    email = "test@test.com"
    password = "password"
    registration_json = {
        "user": {
            "username": username,
            "email": email,
            "password": password,
        }
    }
    response = await client.post(
        app.url_path_for("auth:register"),
        json=registration_json,
    )
    assert response.status_code == status.HTTP_201_CREATED

    user_created = await UsersRepository(get_scoped_session).get_user_by_username(username)
    assert user_created.username == username
    assert user_created.email == email
    assert user_created.check_password(password)


@pytest.mark.parametrize(
    "credentials_field, credentials_value",
    (
        ("username", "unique_username"),
        ("email", "unique@test.com"),
    ),
)
async def test_user_cannot_register_if_some_credentials_are_already_taken(
    app: FastAPI,
    client: AsyncClient,
    credentials_field: str,
    credentials_value: str,
) -> None:
    registration_json = {
        "user": {
            "username": "username",
            "email": "test@test.com",
            "password": "password",
        }
    }
    registration_json["user"][credentials_field] = credentials_value

    response = await client.post(
        app.url_path_for("auth:register"),
        json=registration_json,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
