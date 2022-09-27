from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Depends, Query, Response, HTTPException
from starlette import status

from app.api.dependencies.database import get_repository
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UsersRepository
from app.models.tasks import Task, TaskInCreate, TaskInUpdate
from app.models.users import (
    User,
    UserInLogin,
    UserInCreate,
    UserInResponse,
    UserWithToken,
)
from app.services.authentication import authenticate_user_login
from app.services.jwt import create_access_token_for_user
from app.services.secrets import JWT_SECRET_KEY

app = FastAPI()


@app.get("/tasks")
async def get_tasks(
    page_offset: int = Query(1),
    title: Optional[str] = Query(None),
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    tasks = await tasks_repo.get(page_offset=page_offset, title=title)
    if tasks:
        return Response(status_code=status.HTTP_200_OK, content=tasks)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT, content=tasks)


@app.post("/tasks")
async def create_task(
    task_in_create: TaskInCreate,
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    task = Task(id=str(uuid4()), **task_in_create.dict())
    task_created = await tasks_repo.add(task=task)
    return Response(status_code=status.HTTP_201_CREATED, content=task_created)


@app.patch("/tasks")
async def update_task(
    task_id: str,
    task_in_update: TaskInUpdate,
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    task_updated = await tasks_repo.update(
        task_id=task_id, task_in_update=task_in_update
    )
    if task_updated:
        return Response(status_code=status.HTTP_200_OK, content=task_updated)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    tasks_repo: TasksRepository = Depends(get_repository(TasksRepository)),
):
    if await tasks_repo.delete(task_id=task_id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/signup")
async def signup(
    user_in_create: UserInCreate,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    user = await users_repo.create_user(user_in_create)
    if user:
        return Response(status_code=status.HTTP_201_CREATED, content=user)
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/login")
async def login(
    user_in_login: UserInLogin,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    user = await authenticate_user_login(users_repo, user_in_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token_for_user(user, JWT_SECRET_KEY)
    return UserInResponse(
        user=UserWithToken(
            username=user.username,
            email=user.email,
            token=token,
        )
    )


# @app.get("/user")
# async def retrieve_current_user(
#         user: User = Depends(get_current_user_authorizer()),
# ) -> UserInResponse:
#     token = jwt.
