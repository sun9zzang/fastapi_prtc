import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.models.users import UserInDB
from tests.conftest import _TestUserData, log


async def test_user_can_login(
    app: FastAPI,
    client: AsyncClient,
    test_user: UserInDB,
) -> None:
    login_json = {
        "user": {
            "username": _TestUserData.username.value,
            "password": _TestUserData.password.value,
        }
    }
    log.info(f"login_json: {login_json}")

    log.info("attempting login...")
    response = await client.post(app.url_path_for("auth:login"), json=login_json)
    log.info("login succeeded")
    log.info(f"\tresponse: {response.json()}")
    log.info(f"\ttoken: {response.headers.get('authentication')}")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "credentials_field, credentials_value",
    (("username", "wrong_username"), ("password", "wrong_password")),
)
async def test_user_cannot_login_if_credentials_not_correct(
    app: FastAPI,
    client: AsyncClient,
    test_user: UserInDB,
    credentials_field: str,
    credentials_value: str,
) -> None:
    login_json = {
        "user": {
            "username": _TestUserData.username.value,
            "password": _TestUserData.password.value,
        }
    }
    login_json["user"][credentials_field] = credentials_value
    log.info(f"login_json: {login_json}")

    log.info("attempting login...")
    response = await client.post(app.url_path_for("auth:login"), json=login_json)
    log.info("login failed")
    log.info(f"\tresponse: {response.json()}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
