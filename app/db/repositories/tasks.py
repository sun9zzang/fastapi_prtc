from typing import Optional

from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist
from app.db.db_connection import get_scoped_session
from app.models.tasks import Task, TblTasks
from app.services import utils


# noinspection PyMethodMayBeStatic
class TasksRepository(BaseRepository):
    async def get_task_by_id(self, task_id: str) -> Task:
        with get_scoped_session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row is not None:
                # return Task(**task_row_dict)
                return task_row.convert_to_task()
            raise EntityDoesNotExist(
                f"task with id {task_id} does not exist",
            )

    async def retrieve_tasks(
        self,
        *,
        page_offset: int,
        title: Optional[str],
        username: str,
    ) -> list[Task]:
        page_size = 50

        with get_scoped_session() as session:
            task_tbl = (
                session.query(TblTasks)
                .filter(TblTasks.username == username)
                .limit(page_size)
                .offset((page_offset - 1) * page_size)
            )
            if title:
                task_tbl = task_tbl.filter(TblTasks.title.like(f"%{title}%"))

            result = [task_row.convert_to_task() for task_row in task_tbl.all()]

        return result

    async def create_task(self, *, task: Task) -> Task:
        new_task = TblTasks(
            id=task.id,
            title=task.title,
            content=task.content,
            deadline=utils.convert_string_to_datetime(task.deadline),
            username=task.username,
        )

        with get_scoped_session() as session:
            session.add(new_task)

        return task

    async def update_task(self, *, task: Task) -> Task:
        with get_scoped_session() as session:
            task_dict = task.dict()
            task_dict["deadline"] = utils.convert_string_to_datetime(task.deadline)
            try:
                session.query(TblTasks).filter(TblTasks.id == task.id).update(
                    task_dict, synchronize_session="fetch"
                )
            except Exception as e:
                raise EntityDoesNotExist from e

        return task

    async def delete_task(self, *, task_id: str) -> None:
        with get_scoped_session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row is not None:
                session.delete(task_row)
            else:
                raise EntityDoesNotExist(
                    f"task with id {task_id} does not exist",
                )
