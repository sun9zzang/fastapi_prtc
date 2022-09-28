from typing import Optional
from datetime import timezone

from fastapi import Query

from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist
from app.models.tasks import Task, TaskInUpdate, TblTasks
from app.models.users import User


class TasksRepository(BaseRepository):
    async def get_task_by_id(self, task_id: str) -> Task:
        with self.session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row:
                return Task(**task_row.__dict__)
            raise EntityDoesNotExist(
                f"task with id {task_id} does not exist",
            )

    async def get_tasks(
        self,
        *,
        page_offset: int = Query(1),
        title: Optional[str] = Query(None),
        user: User,
    ) -> list[Task]:
        page_size = 50

        with self.session() as session:
            task_tbl = (
                session.query(TblTasks)
                .filter(TblTasks.username == user.username)
                .limit(page_size)
                .offset((page_offset - 1) * page_size)
            )
            if title:
                task_tbl = task_tbl.filter(TblTasks.title.like(f"%{title}%"))

            result = [Task(**row.__dict__) for row in task_tbl.all()]
            return result

    async def create_task(self, task: Task) -> Task:
        new_task = TblTasks(
            id=task.id,
            title=task.title,
            content=task.content,
            deadline=task.deadline.astimezone(timezone.utc),
            username=task.username,
        )
        with self.session() as session:
            session.add(new_task)

        return task

    async def update_task(self, task_in_update: TaskInUpdate) -> Task:
        with self.session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_in_update.id).first()
            if task_row:
                task_row.update(**task_in_update.dict(), synchronize_session="fetch")
                return Task(**task_row.__dict__)
            raise EntityDoesNotExist(
                f"task with id {task_in_update.id} does not exist",
            )

    async def delete_task(self, task_id: str) -> None:
        with self.session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row:
                session.delete(task_row)
            else:
                raise EntityDoesNotExist(
                    f"task with id {task_id} does not exist",
                )
