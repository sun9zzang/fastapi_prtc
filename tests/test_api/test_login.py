import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.models.users import UserInDB


def test_user_can_login(
    app: FastAPI,
    client: TestClient,
    test_user: UserInDB,
) -> None:
    login_json = {
        "user": {
            "username": "test@test.com",
            "password": "password",
        }
    }

    response = client.post(app.url_path_for("auth:login"), json=login_json)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "credentials_field, credentials_value",
    (("email", "wrong@test.com"), ("password", "wrong_password")),
)
def test_user_cannot_login_if_credentials_not_correct(
    app: FastAPI,
    client: TestClient,
    credentials_field: str,
    credentials_value: str,
) -> None:
    login_json = {
        "user": {
            "username": "test@test.com",
            "password": "password",
        }
    }
    login_json["user"][credentials_field] = credentials_value

    response = client.post(app.url_path_for("auth:login"), json=login_json)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
