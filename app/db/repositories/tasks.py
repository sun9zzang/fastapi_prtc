from typing import Optional
from datetime import timezone

from fastapi import Query, Response

from app.db.repositories.base import BaseRepository
from app.models import Task, TasksInDB


class TasksRepository(BaseRepository):

    def get(
        self, page_offset: int = Query(1), title: Optional[str] = Query(None)
    ):
        page_size = 50

        with self.session() as session:
            query = session.query(TasksInDB).limit(page_size).offset((page_offset - 1) * page_size)
            if title:
                query = query.filter(TasksInDB.title.like(f"%{title}%"))

            result = [row.__dict__ for row in query.all()]
            return result

    def add(self, task: Task):
        new_task = TasksInDB(
            id=task.id,
            title=task.title,
            content=task.content,
            deadline=task.deadline.astimezone(timezone.utc),
        )
        with self.session() as session:
            session.add(new_task)

        return task.dict()

    def delete(self, task_id: str):
        with self.session() as session:
            query = session.query(TasksInDB).filter(TasksInDB.id == task_id).first()
            if not query:
                return Response(status_code=404)
            session.delete(query)

        return Response(status_code=204)
