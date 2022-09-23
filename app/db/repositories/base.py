from typing import Callable

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db_session: Callable[..., Session]) -> None:
        self.session = db_session
