from enum import Enum

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.db.repositories.users import UsersRepository
from app.models.users import UserInDB, UserInResponse
from tests.conftest import _TestUserData, log, _test_user_create, _test_user_withdraw


class _TestUserRouteName(Enum):
    retrieve_current_user = "users:retrieve-current-user"
    update_current_user = "users:update-current-user"
    withdraw_current_user = "users:withdraw-current-user"


@pytest.mark.parametrize(
    "api_method, route_name",
    (
        ("POST", _TestUserRouteName.retrieve_current_user.value),
        ("PUT", _TestUserRouteName.update_current_user.value)
    ),
)
async def test_user_cannot_access_own_profile_if_not_logged_in(
    app: FastAPI,
    client: AsyncClient,
    api_method: str,
    route_name: str,
) -> None:
    log.info("attempting to access profile...")
    response = await client.request(
        api_method,
        app.url_path_for(route_name),
    )
    log.info("access denied")
    log.info(f"\tresponse: {response.json()}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "api_method, route_name",
    (
        ("POST", _TestUserRouteName.retrieve_current_user.value),
        ("PUT", _TestUserRouteName.update_current_user.value)
    ),
)
async def test_user_cannot_access_own_profile_if_token_is_wrong(
    app: FastAPI,
    client: AsyncClient,
    api_method: str,
    route_name: str,
    wrong_authorization_header: str,
) -> None:
    log.info("attempting to access profile...")
    response = await client.request(
        api_method,
        app.url_path_for(route_name),
        headers={"Authorization": wrong_authorization_header},
    )
    log.info("access denied")
    log.info(f"\tresponse: {response.json()}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_can_retrieve_own_profile(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
    token: str,
) -> None:
    log.info("attempting to access profile...")
    response = await authorized_client.post(
        app.url_path_for(_TestUserRouteName.retrieve_current_user.value)
    )
    log.info("access succeeded")
    user_retrieved = response.json()
    log.info(f"response: {user_retrieved}")
    assert response.status_code == status.HTTP_200_OK

    log.info("collating username...")
    user_in_response = UserInResponse(**user_retrieved)
    assert user_in_response.user.username == test_user.username


@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("username", "new_username"),
        ("email", "new_email@test.com"),
    ),
)
async def test_user_can_update_own_profile(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
    update_field: str,
    update_value: str,
) -> None:
    log.info("attempting to update profile...")
    response = await authorized_client.put(
        app.url_path_for(_TestUserRouteName.update_current_user.value),
        json={update_field: update_value},
    )
    log.info("update succeeded")
    log.info(f"response: {response.json()}")
    assert response.status_code == status.HTTP_200_OK

    log.info("collating updated data...")
    user_in_response = UserInResponse(**response.json()).dict()
    assert user_in_response["user"][update_field] == update_value

    if update_field == "username":
        await _test_user_withdraw(username=update_value)  # todo user uid 추가하기


async def test_user_can_change_password(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
) -> None:
    new_password = "new_password"
    log.info("attempting to update password...")
    response = await authorized_client.put(
        app.url_path_for(_TestUserRouteName.update_current_user.value),
        json={"password": new_password},
    )
    log.info("update succeeded")
    user_updated = response.json()
    log.info(f"response: {user_updated}")
    assert response.status_code == status.HTTP_200_OK

    log.info("checking password...")
    user_in_db = await UsersRepository().get_user_by_username(
        username=user_updated["user"]["username"]
    )
    assert user_in_db.check_password(new_password)


@pytest.fixture
async def _test_user_taken() -> UserInDB:
    user_dict = {
        "username": "taken_username",
        "email": "taken@test.com",
        "password": "password",
    }
    user = await _test_user_create(user=user_dict)

    yield user

    await _test_user_withdraw(user.username)


@pytest.mark.parametrize(
    "credentials_field, credentials_value",
    (
        ("username", "taken_username"),
        ("email", "taken@test.com"),
    ),
)
async def test_user_cannot_take_already_taken_credentials(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
    _test_user_taken: UserInDB,
    credentials_field: str,
    credentials_value: str,
) -> None:
    log.info("attempting to update profile...")
    log.info(f"{credentials_field}: {test_user.dict()[credentials_field]} -> {credentials_value}")
    response = await authorized_client.put(
        app.url_path_for(_TestUserRouteName.update_current_user.value),
        json={credentials_field: credentials_value},
    )
    log.info("update failed")
    log.info(f"response: {response.json()}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_user_cannot_withdraw_if_token_is_wrong(
    app: FastAPI,
    client: AsyncClient,
    test_user: UserInDB,
    wrong_authorization_header: str,
) -> None:
    log.info("attempting to withdraw user with wrong token...")
    response = await client.delete(
        app.url_path_for(_TestUserRouteName.withdraw_current_user.value),
        headers={"Authorization": wrong_authorization_header},
    )
    log.info("user withdrawal failed - access denied")
    log.info(f"response: {response.json()}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_can_withdraw(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
) -> None:
    log.info("attempting to withdraw user")
    response = await authorized_client.delete(
        app.url_path_for(_TestUserRouteName.withdraw_current_user.value)
    )
    log.info("user withdrawal succeeded")
    assert response.status_code == status.HTTP_204_NO_CONTENT
