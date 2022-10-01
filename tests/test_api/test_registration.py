import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.db.repositories.users import UsersRepository
from app.models.users import User
from tests.conftest import _TestUserData, log


async def test_user_can_registration(
    app: FastAPI,
    client: AsyncClient,
    test_user_withdraw: None,
) -> None:
    registration_json = {"user": _TestUserData.dict()}
    log.info(f"registration_json: {registration_json}")

    log.info("attempting registration...")
    response = await client.post(
        app.url_path_for("auth:register"),
        json=registration_json,
    )
    log.info("registration succeeded")
    log.info(f"\tresponse: {response.json()}")
    assert response.status_code == status.HTTP_201_CREATED

    log.info("retrieving user data from DB...")
    user_in_db = await UsersRepository().get_user_by_username(_TestUserData.username.value)
    log.info(f"\tuser_in_db: {user_in_db.__repr__()}")

    assert user_in_db.username == _TestUserData.username.value
    assert user_in_db.email == _TestUserData.email.value
    assert user_in_db.check_password(_TestUserData.password.value)


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
    test_user: User,
    credentials_field: str,
    credentials_value: str,
) -> None:
    registration_json = {"user": _TestUserData.dict()}
    registration_json["user"][credentials_field] = credentials_value
    log.info(f"registration_json: {registration_json}")

    log.info("attempting registration...")
    response = await client.post(
        app.url_path_for("auth:register"),
        json=registration_json,
    )
    log.info("registration failed")
    log.info(f"\tresponse: {response.json()}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
