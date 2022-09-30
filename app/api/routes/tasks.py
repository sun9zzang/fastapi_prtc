from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Query, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.db.repositories.tasks import TasksRepository
from app.db.errors import EntityDoesNotExist
from app.models.tasks import Task, TaskInCreate, TaskInUpdate
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
    page_offset: int = Query(1),
    title: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    tasks = await tasks_repo.retrieve_tasks(
        username=current_user.username,
        page_offset=page_offset,
        title=title,
    )

    return tasks


@router.post(
    "",
    name="tasks:create-task",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskInCreate = Body(..., embed=True),
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    task_created = Task(
        id=str(uuid4()),
        title=task.title,
        content=task.content,
        deadline=task.deadline,
        username=current_user.username,
    )
    await tasks_repo.create_task(task=task_created)

    return task_created


@router.put(
    "",
    name="tasks:update-task",
    response_model=Task,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task: TaskInUpdate = Body(..., embed=True),
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    if current_user.username != task.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    task_updated = await tasks_repo.update_task(task=task)

    return task_updated


@router.delete(
    "/{task_id}", name="tasks:delete-task", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user_authorizer()),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    task = None
    try:
        task = await tasks_repo.get_task_by_id(task_id=task_id)
    except EntityDoesNotExist as existence_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=existence_error.args[0],
        ) from existence_error

    if current_user.username != task.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    try:
        await tasks_repo.delete_task(task_id=task_id)
    except EntityDoesNotExist as existence_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=existence_error.args[0],
        ) from existence_error
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
