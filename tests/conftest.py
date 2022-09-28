from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import JWT_SECRET_KEY
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UsersRepository
from app.db.db_connection import session_scope
from app.models.tasks import Task, TaskInCreate
from app.models.users import UserInCreate, UserInDB
from app.services import jwt


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application

    return get_application()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def test_user() -> UserInDB:
    return await UsersRepository(session_scope).create_user(
        user_in_create=UserInCreate(
            username="username",
            email="test@test.com",
            password="password",
        )
    )


@pytest.fixture
async def test_task(test_user: UserInDB) -> Task:
    return await TasksRepository(session_scope).create_task(
        task=Task(
            id=str(uuid4()),
            title="test_title",
            content="test_content",
            deadline=datetime.now(),
            username=test_user.username,
        ),
    )


@pytest.fixture
def token(test_user: UserInDB) -> str:
    return jwt.create_access_token_for_user(test_user, JWT_SECRET_KEY)


@pytest.fixture(
    params=(
        "",
        "wrong-token",
        "Token wrong-token",
        "JWT wrong-token",
        "Bearer wrong-token",
    )
)
def wrong_authorization_header(request) -> str:
    return request.param


@pytest.fixture
def authorized_client(client: TestClient, token: str) -> TestClient:
    client.headers.update({"Authorization": f"Token {token}"})
    return client
