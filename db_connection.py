from sqlalchemy import Column, String, DateTime, create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

from contextlib import contextmanager

Base = declarative_base()
engine = create_engine(
    "mysql+pymysql://admin:pwd12345@todo-list-rds.cmlkx2wu51ea.ap-northeast-2.rds.amazonaws.com:3306/todo_list",
    echo=True, future=True)
Session = sessionmaker(bind=engine)


class TblTasks(Base):
    __tablename__ = "tbl_tasks"

    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(String)
    deadline = Column(DateTime)

    def __repr__(self):
        return f"TblTasks(uid={self.id}, title={self.title}, content={self.content}, deadline={self.deadline})"


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
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
