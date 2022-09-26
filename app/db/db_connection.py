import json
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

from app.secrets.secrets import get_secret

db_url = {
    "aws_rds": json.loads(get_secret())["todo_list.db_connection_url"],
    "local": "mysql+pymysql://root:pwd12345@localhost:3306/todo_list",
}

Base = declarative_base()
engine = create_engine(
    db_url["local"],
    echo=True,
    future=True,
)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def obj_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
