from typing import Callable, Type

from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.db_connection import session_scope


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[Session], BaseRepository]:
    def _get_repo() -> BaseRepository:
        return repo_type(session_scope)

    return _get_repo
