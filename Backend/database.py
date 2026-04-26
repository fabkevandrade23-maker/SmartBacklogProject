# (5) py part5
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://user:password@localhost/smartbacklog"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# (6) py part6
from sqlalchemy import Column, Integer, String

class Task(Base):
    _tablename_ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    status = Column(String)
    priority = Column(Integer)


# (14) py part14
from sqlalchemy import Column, Integer, String, ForeignKey

class Task(Base):
    _tablename_ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    status = Column(String)
    priority = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))


# (15) py part15
from sqlalchemy import Column, Integer, String, ForeignKey

class Task(Base):
    _tablename_ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    status = Column(String)
    priority = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

