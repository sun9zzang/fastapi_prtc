from uuid import uuid4
import logging

import pytest
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient

from app.core import config
from app.db.errors import EntityDoesNotExist
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UsersRepository
from app.models.tasks import Task
from app.models.users import User, UserInCreate, UserInDB
from app.services import jwt

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

test_user_data = {
    "username": "username",
    "email": "test@test.com",
    "password": "password",
}


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
        log.info("[test_user] creating user...")
        user = await UsersRepository().create_user(
            user=UserInCreate(**test_user_data)
        )
        log.info("[test_user] user created")
    except IntegrityError:
        log.warning("[test_user] user already exists. retrieving user...")
        user = await UsersRepository().get_user_by_username(
            "username"
        )
        log.info("[test_user] user retrieved")
    finally:
        yield user

        log.info("[test_user] withdrawing user...")
        await UsersRepository().withdraw_user(username=user.username)
        log.info("[test_user] user withdrew")


@pytest.fixture
async def test_task(test_user: UserInDB) -> Task:
    task = Task(
        id=str(uuid4()),
        title="test_title",
        content="test_content",
        deadline="2123-04-05 16:07:08.123456",
        username=test_user.username,
    )
    log.info("[test_task] creating task...")
    task = await TasksRepository().create_task(task=task)
    log.info(f"[test_task] task created - task_id: {task.id}")

    yield task

    try:
        log.info("[test_task] deleting task...")
        await TasksRepository().delete_task(task_id=task.id)
    except EntityDoesNotExist as existence_error:
        log.info(f"[test_task] failed to delete task\n\ttask.id: {task.id}\n\terror: {existence_error}")
        raise EntityDoesNotExist from existence_error


@pytest.fixture
def token() -> str:
    user = User(username=test_user_data["username"], email=test_user_data["email"])

    log.info("creating token...")
    token = jwt.create_access_token_for_user(user, config.JWT_SECRET_KEY)
    log.info(f"token created\n\ttoken: {token}")

    return token


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
    log.info("updating header for authorizing client...")
    client.headers.update({"Authorization": f"Token {token}"})
    log.info(f"client authorized\n\ttoken: {token}")

    return client
