import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.db.repositories.users import UsersRepository
from app.db.db_connection import session_scope


def test_user_can_registration(
    app: FastAPI,
    client: TestClient,
) -> None:
    username = "username"
    email = "test@test.com"
    password = "password"
    registration_json = {
        "user_in_create": {
            "username": username,
            "email": email,
            "password": password,
        }
    }
    response = client.post(
        app.url_path_for("auth:register"),
        json=registration_json,
    )
    assert response.status_code == status.HTTP_201_CREATED

    user_created = await UsersRepository(session_scope).get_user_by_username(username)
    assert user_created.username == username
    assert user_created.email == email
    assert user_created.check_password(password)


@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (
        ("username", "unique_username"),
        ("email", "unique@test.com"),
    ),
)
def test_user_cannot_register_if_some_credentials_are_already_taken(
    app: FastAPI,
    client: TestClient,
    credentials_part: str,
    credentials_value: str,
) -> None:
    registration_json = {
        "user_in_create": {
            "username": "username",
            "email": "test@test.com",
            "password": "password",
        }
    }
    registration_json["user_in_create"][credentials_part] = credentials_value

    response = client.post(
        app.url_path_for("auth:register"),
        json=registration_json,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
