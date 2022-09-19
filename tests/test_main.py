from fastapi.testclient import TestClient
import json

import main
from main import app

client = TestClient(app)


def test_get_tasks():
    response = client.get("/tasks")
    print(response.json())
    print(type(response.json()))
    assert response.status_code == 200


def test_get_tasks_empty():
    response = client.get("/tasks")
    assert response.json() != "[]"


def test_get_tasks_page_size():
    response = client.get("/tasks")
    table_dict = json.loads(response.json())
    assert len(table_dict) == main.page_size


def test_add_task():
    response = client.post("/tasks")
    print(response.json())
    assert response.status_code == 200


def test_delete_task():
    task_id = input("Enter task id you want to delete: ")
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
