from typing import Callable, Type

from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.db_connection import get_scoped_session


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[Session], BaseRepository]:
    def _get_repo() -> BaseRepository:
        return repo_type(get_scoped_session)

    return _get_repo
