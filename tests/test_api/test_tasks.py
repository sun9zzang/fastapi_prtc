from datetime import datetime

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.db.repositories.tasks import TasksRepository
from app.db.db_connection import get_scoped_session
from app.db.errors import EntityDoesNotExist
from app.models.tasks import Task


@pytest.mark.parametrize(
    "api_method, route_name",
    (
        ("POST", "tasks:create-task"),
        ("GET", "tasks:retrieve-tasks"),
        ("PUT", "tasks:update-task"),
        ("DELETE", "tasks:delete-task"),
    ),
)
def test_user_cannot_access_task_if_not_logged_in(
    app: FastAPI,
    client: TestClient,
    api_method: str,
    route_name: str,
) -> None:
    response = client.request(
        api_method,
        app.url_path_for(route_name),
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
def test_user_cannot_retrieve_task_if_token_is_wrong(
    app: FastAPI,
    client: TestClient,
    test_task: Task,
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


def test_user_can_create_task(
    app: FastAPI,
    authorized_client: TestClient,
    test_task: Task,
) -> None:
    response = authorized_client.post(
        app.url_path_for("tasks:create-task"),
        json=test_task.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED

    task_created = TasksRepository(get_scoped_session).get_task_by_id(test_task.id)
    assert task_created


def test_user_can_retrieve_task(
    app: FastAPI,
    authorized_client: TestClient,
) -> None:
    response = authorized_client.get(app.url_path_for("tasks:retrieve-tasks"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("title", "new_title"),
        ("content", "new_content"),
        ("deadline", datetime(year=2099, month=1, day=1)),
    ),
)
def test_user_can_update_task(
    app: FastAPI,
    authorized_client: TestClient,
    test_task: Task,
    update_field: str,
    update_value: str,
) -> None:
    task_dict = test_task.dict()
    task_dict.update({update_field: update_value})
    response = authorized_client.put(
        app.url_path_for("tasks:update-task"),
        json=task_dict,
    )
    assert response.status_code == status.HTTP_200_OK

    task_in_response = Task(**response.json()).dict()
    assert task_in_response[update_field] == update_value


def test_user_can_delete_task(
    app: FastAPI,
    authorized_client: TestClient,
    test_task: Task,
) -> None:
    response = authorized_client.delete(
        app.url_path_for("tasks:delete-task", task_id=test_task.id)
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    task_deleted = None
    try:
        task_deleted = TasksRepository(get_scoped_session).get_task_by_id(
            task_id=test_task.id
        )
    except EntityDoesNotExist:
        pass
    finally:
        assert task_deleted is None
