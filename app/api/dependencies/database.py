from typing import Callable, Type

from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[Session], BaseRepository]:
    def _get_repo() -> BaseRepository:
        return repo_type()

    return _get_repo
