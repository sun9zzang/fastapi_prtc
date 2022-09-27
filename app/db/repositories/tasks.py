from typing import Optional
from datetime import timezone

from fastapi import Query

from app.db.repositories.base import BaseRepository
from app.models.tasks import Task, TaskInUpdate, TblTasks


class TasksRepository(BaseRepository):
    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        with self.session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row:
                return Task(**task_row.__dict__)
            else:
                return None

    async def get(self, page_offset: int = Query(1), title: Optional[str] = Query(None)) -> list[dict]:
        page_size = 50

        with self.session() as session:
            task_tbl = (
                session.query(TblTasks)
                .limit(page_size)
                .offset((page_offset - 1) * page_size)
            )
            if title:
                task_tbl = task_tbl.filter(TblTasks.title.like(f"%{title}%"))

            result = [row.__dict__ for row in task_tbl.all()]
            return result

    async def add(self, task: Task) -> dict:
        new_task = TblTasks(
            id=task.id,
            title=task.title,
            content=task.content,
            deadline=task.deadline.astimezone(timezone.utc),
        )
        with self.session() as session:
            session.add(new_task)

        return task.dict()

    async def update(self, task_id: str, task_in_update: TaskInUpdate) -> Optional[dict]:
        with self.session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row:
                task_row.update(**task_in_update.dict(), synchronize_session="fetch")
                return task_row.__dict__
            else:
                return None

    async def delete(self, task_id: str) -> bool:
        with self.session() as session:
            task_row = session.query(TblTasks).filter(TblTasks.id == task_id).first()
            if task_row:
                session.delete(task_row)
                return True

        return False
