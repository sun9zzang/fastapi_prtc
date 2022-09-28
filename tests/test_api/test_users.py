import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.db.repositories.users import UsersRepository
from app.db.db_connection import session_scope
from app.models.users import UserInDB, UserInResponse


@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "users:get-current-user"), ("PUT", "users:update-current-user")),
)
def test_user_cannot_access_own_profile_if_not_logged_in(
    app: FastAPI,
    client: TestClient,
    api_method: str,
    route_name: str,
) -> None:
    response = client.request(api_method, app.url_path_for(route_name))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "users:get_current-user"), ("PUT", "users:update-current-user")),
)
def test_user_cannot_retrieve_own_profile_if_token_is_wrong(
    app: FastAPI,
    client: TestClient,
    api_method: str,
    route_name: str,
    wrong_authorization_header: str,
) -> None:
    response = client.request(
        api_method,
        app.url_path_for(route_name),
        headers={"Authorization": wrong_authorization_header},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_can_retrieve_own_profile(
    app: FastAPI,
    authorized_client: TestClient,
    test_user: UserInDB,
    token: str,
) -> None:
    response = authorized_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == status.HTTP_200_OK

    user_in_response = UserInResponse(**response.json())
    assert user_in_response.user.username == test_user.username


@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("username", "new_username"),
        ("email", "new_email@test.com"),
    ),
)
def test_user_can_update_own_profile(
    app: FastAPI,
    authorized_client: TestClient,
    update_field: str,
    update_value: str,
) -> None:
    response = authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {update_field: update_value}},
    )
    assert response.status_code == status.HTTP_200_OK

    user_in_response = UserInResponse(**response.json()).dict()
    assert user_in_response["user"][update_field] == update_value


def test_user_can_change_password(
    app: FastAPI,
    authorized_client: TestClient,
    token: str,
) -> None:
    response = authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {"password": "new_password"}},
    )
    assert response.status_code == status.HTTP_200_OK

    user_in_response = UserInResponse(**response.json())
    user = await UsersRepository(session_scope).get_user_by_username(
        username=user_in_response.user.username
    )
    assert user.check_password("new_password")


@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (("username", "taken_username"), ("email", "taken@test.com")),
)
def test_user_cannot_take_already_taken_credentials(
    app: FastAPI,
    authorized_client: TestClient,
    token: str,
    credentials_part: str,
    credentials_value: str,
) -> None:
    user_dict = {
        "username": "not_taken_username",
        "password": "password",
        "email": "not_taken@test.com",
    }
    user_dict.update({credentials_part: credentials_value})
    await UsersRepository(session_scope).create_user(**user_dict)

    response = authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {credentials_part: credentials_value}},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_cannot_withdraw_if_token_is_wrong(
    app: FastAPI,
    client: TestClient,
    wrong_authorization_header: str,
) -> None:
    response = client.delete(
        app.url_path_for("users:withdraw-current-user"),
        headers={"Authorization": wrong_authorization_header},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_can_withdraw(
    app: FastAPI,
    authorized_client: TestClient,
    test_user: UserInDB,
) -> None:
    response = authorized_client.delete(app.url_path_for("users:withdraw-current-user"))
    assert response.status_code == status.HTTP_204_NO_CONTENT

