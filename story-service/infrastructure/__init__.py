
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from user_bot.settings import settings

__all__ = [
    "session_maker",
]


engine = create_async_engine(settings.db.url, echo=False, pool_recycle=1800, pool_timeout=30)
session_maker = async_sessionmaker(engine, expire_on_commit=False)
