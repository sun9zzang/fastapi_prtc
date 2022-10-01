from uuid import uuid4
import logging
from enum import Enum
from typing import Optional

import pytest
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient

from app.core.config import JWT_SECRET_KEY
from app.db.errors import EntityDoesNotExist
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UsersRepository
from app.models.tasks import Task
from app.models.users import User, UserInCreate, UserInDB
from app.services import jwt

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


class _TestUserData(Enum):
    username = "username"
    email = "test@test.com"
    password = "password"

    @staticmethod
    def dict() -> dict:
        return {e.name: e.value for e in _TestUserData}


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


async def _test_user_create(user: Optional[dict] = None) -> UserInDB:
    # user_in_create = None
    if user is None:
        user_in_create = UserInCreate(**_TestUserData.dict())
    else:
        user_in_create = UserInCreate(**user)

    user_in_db = None
    try:
        log.info(f"attempting to create test user - username: {user_in_create.username}")
        user_in_db = await UsersRepository().create_user(
            user=user_in_create
        )
        log.info("user created successfully")
    except IntegrityError:
        log.warning(f"username: {user_in_create.username} already exists. "
                    f"attempting to retrieve user...")
        user_in_db = await UsersRepository().get_user_by_username(user_in_create.username)
        log.info("user retrieved successfully")
    finally:
        return user_in_db


async def _test_user_withdraw(username: Optional[str] = _TestUserData.username.value) -> None:
    log.info(f"withdrawing user... - username: {username}")
    await UsersRepository().withdraw_user(username=username)
    log.info("user withdrawal succeeded")


@pytest.fixture
async def test_user_create() -> UserInDB:
    yield await _test_user_create()


@pytest.fixture
async def test_user_withdraw() -> None:
    yield None
    await _test_user_withdraw()


@pytest.fixture
async def test_user() -> UserInDB:
    user = await _test_user_create()

    yield user

    await _test_user_withdraw()


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
        log.info(
            f"[test_task] failed to delete task"
            f"\n\ttask.id: {task.id}\n\terror: {existence_error}"
        )
        raise EntityDoesNotExist from existence_error


@pytest.fixture
def token() -> str:
    user = User(username=_TestUserData.username.value, email=_TestUserData.email.value)

    log.info("creating token...")
    token = jwt.create_access_token_for_user(user, JWT_SECRET_KEY)
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
