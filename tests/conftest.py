from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient

from app.core import config
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UsersRepository
from app.db.db_connection import get_scoped_session
from app.models.tasks import Task
from app.models.users import UserInCreate, UserInDB
from app.services import jwt


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application

    return get_application()


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
async def test_user() -> UserInDB:
    user = None
    try:
        user = await UsersRepository(get_scoped_session).create_user(
            user=UserInCreate(
                username="username",
                email="test@test.com",
                password="password",
            )
        )
    except IntegrityError:
        user = await UsersRepository(get_scoped_session).get_user_by_username("username")
    finally:
        yield user
        await UsersRepository(get_scoped_session).withdraw_user(username=user.username)


@pytest.fixture
async def test_task(test_user: UserInDB) -> Task:
    task = await TasksRepository(get_scoped_session).create_task(
        task=Task(
            id=str(uuid4()),
            title="test_title",
            content="test_content",
            deadline=datetime.strptime("2123-04-05 16:07:08.123456", config.DATETIME_FORMAT_STRING),
            username=test_user.username,
        ),
    )
    task.deadline = task.deadline.strftime(config.DATETIME_FORMAT_STRING)

    yield task

    await TasksRepository(get_scoped_session).delete_task(task_id=task.id)


@pytest.fixture
def token(test_user: UserInDB) -> str:
    return jwt.create_access_token_for_user(test_user, config.JWT_SECRET_KEY)


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
def authorized_client(client: AsyncClient, token: str) -> AsyncClient:
    client.headers.update({"Authorization": f"Token {token}"})
    return client
