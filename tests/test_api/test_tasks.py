from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.core import config
from app.db.repositories.tasks import TasksRepository
from app.db.db_connection import get_scoped_session
from app.db.errors import EntityDoesNotExist
from app.models.tasks import Task
from app.models.users import UserInDB


@pytest.mark.parametrize(
    "api_method, route_name, additional_url",
    (
        ("POST", "tasks:create-task", ""),
        ("GET", "tasks:retrieve-tasks", ""),
        ("PUT", "tasks:update-task", ""),
        ("DELETE", "tasks:delete-task", "/"),
    ),
)
async def test_user_cannot_access_task_if_not_logged_in(
    app: FastAPI,
    client: AsyncClient,
    api_method: str,
    route_name: str,
    additional_url: str,
) -> None:
    response = await client.request(
        api_method,
        app.url_path_for(route_name) + additional_url,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "api_method, route_name",
    (
        ("POST", "tasks:create-task"),
        ("GET", "tasks:retrieve-tasks"),
        ("PUT", "tasks:update-task"),
        ("DELETE", "tasks:delete-task"),
    ),
)
async def test_user_cannot_retrieve_task_if_token_is_wrong(
    app: FastAPI,
    client: AsyncClient,
    api_method: str,
    route_name: str,
    wrong_authorization_header: str,
) -> None:
    response = await client.request(
        api_method,
        app.url_path_for(route_name),
        headers={"Authorization": wrong_authorization_header},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_can_create_task(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
) -> None:
    task_json = {
        "task": {
            "title": "test_user_can_create_task",
            "content": "test_content",
            "deadline": "2123-04-05 16:07:08.123456",
            "username": test_user.username,
        }
    }
    response = await authorized_client.post(
        app.url_path_for("tasks:create-task"),
        json=task_json,
    )
    assert response.status_code == status.HTTP_201_CREATED

    task_created_id = response.json()["id"]
    task_created = await TasksRepository(get_scoped_session).get_task_by_id(
        task_created_id
    )
    assert task_created

    await TasksRepository(get_scoped_session).delete_task(task_id=task_created_id)


async def test_user_can_retrieve_task(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_task: Task,
) -> None:
    response = await authorized_client.get(app.url_path_for("tasks:retrieve-tasks"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("title", "new_title"),
        ("content", "new_content"),
        ("deadline", "2099-09-09 09:09:09.999999"),
    ),
)
async def test_user_can_update_task(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_task: Task,
    update_field: str,
    update_value: str,
) -> None:
    task_dict = {"task": test_task.dict()}
    task_dict["task"].update({update_field: update_value})
    response = await authorized_client.put(
        app.url_path_for("tasks:update-task"),
        json=task_dict,
    )
    assert response.status_code == status.HTTP_200_OK

    task_updated = await TasksRepository(get_scoped_session).get_task_by_id(test_task.id)
    assert task_dict["task"]["title"] == task_updated.title
    assert task_dict["task"]["content"] == task_updated.content
    assert task_dict["task"]["deadline"] == task_updated.title



async def test_user_can_delete_task(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
) -> None:
    task = Task(
        id=str(uuid4()),
        title="test_user_can_delete_task",
        content="test_content",
        deadline=datetime.strptime(
            "2123-04-05 16:07:08.123456", config.DATETIME_FORMAT_STRING
        ),
        username=test_user.username,
    )
    await TasksRepository(get_scoped_session).create_task(task=task)

    response = await authorized_client.delete(
        app.url_path_for("tasks:delete-task", task_id=task.id)
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    try:
        await TasksRepository(get_scoped_session).delete_task(task_id=task.id)
    except EntityDoesNotExist:
        pass
    else:
        raise AssertionError(f"task with id {task.id} was not deleted")
