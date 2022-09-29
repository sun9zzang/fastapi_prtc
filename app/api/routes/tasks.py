from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, Query, status
from fastapi.exceptions import RequestValidationError

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.db.repositories.tasks import TasksRepository
from app.db.errors import EntityDoesNotExist
from app.models.tasks import Task, TaskInCreate, TaskInUpdate, TaskInDelete
from app.models.users import User


router = APIRouter()


@router.get(
    "",
    response_model=list[Task],
    name="tasks:retrieve-tasks",
    status_code=status.HTTP_200_OK,
)
async def retrieve_tasks(
    *,
    page_offset: int = Query(default=1),
    title: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    tasks = await tasks_repo.get_tasks(
        page_offset=page_offset, title=title, username=current_user.username
    )

    return tasks


@router.post(
    "",
    response_model=Task,
    name="tasks:create-task",
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskInCreate,
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    if current_user.username != task.username:
        raise RequestValidationError("invalid user data")

    task_created = Task(
        id=str(uuid4()),
        title=task.title,
        content=task.content,
        deadline=task.deadline,
        username=task.username,
    )
    await tasks_repo.create_task(task=task_created)

    return task_created


@router.put(
    "",
    response_model=Task,
    name="tasks:update-task",
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task: TaskInUpdate,
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    if current_user.username != task.username:
        raise RequestValidationError("invalid user data")

    await tasks_repo.update_task(task=task)

    return task


@router.delete(
    "/{task_id}",
    name="tasks:delete-task",
)
async def delete_task(
    task: TaskInDelete,
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    if current_user.username != task.username:
        raise RequestValidationError("invalid user data")

    try:
        await tasks_repo.delete_task(task_id=task.id)
    except EntityDoesNotExist as existence_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=existence_error.args[0],
        ) from existence_error
    finally:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
