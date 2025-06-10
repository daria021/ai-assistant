from sqlalchemy.ext.asyncio import async_sessionmaker

from shared.infrastructure.main_db import get_sessionmaker


def get_session_maker() -> async_sessionmaker:
    return get_sessionmaker()
