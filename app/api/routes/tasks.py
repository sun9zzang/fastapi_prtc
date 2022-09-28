from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies.database import get_repository
from app.db.repositories.tasks import TasksRepository
from app.models.tasks import Task, TaskInCreate, TaskInUpdate


router = APIRouter()


@router.get("")
async def get_tasks(
    page_offset: int = Query(default=1),
    title: Optional[str] = Query(default=None),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    tasks = await tasks_repo.get_tasks(page_offset=page_offset, title=title)
    if tasks:
        return Response(status_code=status.HTTP_200_OK, content=tasks)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT, content=tasks)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in_create: TaskInCreate,
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    task = Task(id=str(uuid4()), **task_in_create.dict())
    task_created = await tasks_repo.create_task(task=task)

    return task_created


@router.patch("")
async def update_task(
    task_in_update: TaskInUpdate,
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    task_updated = await tasks_repo.update_task(task_in_update=task_in_update)
    if task_updated:
        return Response(status_code=status.HTTP_200_OK, content=task_updated)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    if await tasks_repo.delete_task(task_id=task_id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
