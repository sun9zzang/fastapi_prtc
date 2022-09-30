from uuid import uuid4
import logging

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.db.repositories.tasks import TasksRepository
from app.models.tasks import Task
from app.models.users import UserInDB

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "api_method, route_name",
    (
        ("POST", "tasks:create-task"),
        ("GET", "tasks:retrieve-tasks"),
        ("PUT", "tasks:update-task"),
    ),
)
async def test_user_cannot_access_task_if_not_logged_in(
    app: FastAPI,
    client: AsyncClient,
    test_task: Task,
    api_method: str,
    route_name: str,
) -> None:
    response = await client.request(
        api_method,
        app.url_path_for(route_name),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_cannot_delete_task_if_not_logged_in(
    app: FastAPI,
    client: AsyncClient,
    test_task: Task,
) -> None:
    response = await client.delete(
        app.url_path_for("tasks:delete-task", task_id=test_task.id)
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "api_method, route_name",
    (
        ("POST", "tasks:create-task"),
        ("GET", "tasks:retrieve-tasks"),
        ("PUT", "tasks:update-task"),
    ),
)
async def test_user_cannot_retrieve_task_if_token_is_wrong(
    app: FastAPI,
    client: AsyncClient,
    test_task: Task,
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


async def test_user_cannot_delete_task_if_token_is_wrong(
    app: FastAPI,
    client: AsyncClient,
    test_task: Task,
    wrong_authorization_header: str,
) -> None:
    response = await client.delete(
        app.url_path_for("tasks:delete-task", task_id=test_task.id),
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
    log.info(f"creating new task...\n\ttask_json: {task_json}")
    response = await authorized_client.post(
        app.url_path_for("tasks:create-task"),
        json=task_json,
    )
    log.info(f"task created")
    task_created = response.json()
    log.info(f"\ttask_created: {task_created}")
    assert response.status_code == status.HTTP_201_CREATED

    log.info("deleting task...")
    await TasksRepository().delete_task(task_id=task_created["id"])
    log.info(f"- task deleted - \n\ttask.id={task_created['id']}")


async def test_user_can_retrieve_task(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_task: Task,
) -> None:
    log.info("retrieving task...")
    response = await authorized_client.get(app.url_path_for("tasks:retrieve-tasks"))
    log.info(f"task retrieved\n\t{response.json()}")
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
    log.info(f"updating task...\n\ttask_dict: {task_dict}")
    response = await authorized_client.put(
        app.url_path_for("tasks:update-task"),
        json=task_dict,
    )
    log.info("task updated")
    task_updated = response.json()
    log.info(f"\ttask_updated: {task_updated}")
    assert response.status_code == status.HTTP_200_OK

    assert task_dict["task"]["title"] == task_updated.title
    assert task_dict["task"]["content"] == task_updated.content
    assert task_dict["task"]["deadline"] == task_updated.deadline


async def test_user_can_delete_task(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_task: Task,
) -> None:
    log.info(f"deleting task\n\ttest_task: {test_task}")
    response = await authorized_client.delete(
        app.url_path_for("tasks:delete-task", task_id=test_task.id),
    )
    log.info("task deleted")
    assert response.status_code == status.HTTP_204_NO_CONTENT
