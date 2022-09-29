import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.models.users import UserInDB


async def test_user_can_login(
    app: FastAPI,
    client: AsyncClient,
    test_user: UserInDB,
) -> None:
    login_json = {
        "user": {
            "username": "username",
            "password": "password",
        }
    }
    print(login_json)
    response = await client.post(app.url_path_for("auth:login"), data=login_json)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "credentials_field, credentials_value",
    (("username", "wrong_username"), ("password", "wrong_password")),
)
async def test_user_cannot_login_if_credentials_not_correct(
    app: FastAPI,
    client: AsyncClient,
    credentials_field: str,
    credentials_value: str,
) -> None:
    login_json = {
        "user": {
            "username": "username",
            "password": "password",
        }
    }
    login_json["user"][credentials_field] = credentials_value

    response = await client.post(app.url_path_for("auth:login"), json=login_json)
    print(app.url_path_for("auth:login"))
    print(response.json())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
