from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.services.secrets import get_secret

db_url = {
    "aws_rds": get_secret()["todo_list.db_connection_url"],
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
