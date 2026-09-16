from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Base


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def new_session():
    return Session(bind=get_engine(), expire_on_commit=False)


def init_db():
    Base.metadata.create_all(get_engine())


def get_session():
    with new_session() as session:
        yield session
