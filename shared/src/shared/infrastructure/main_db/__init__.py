from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .migrator import apply_migrations
from .repositories import (
    UserRepository,
    ChatRepository,
    PostRepository,
    StoryRepository,
    SendPostRequestRepository,
    StoryToPublishRepository,
    PostToPublishRepository,
    PublishStoryRequestRepository,
    WorkerMessageRepository,
    ProxyRepository,
    NoFreeProxiesException,
)
from .settings import MainDBSettings

__all__ = [
    "session_maker",
    "UserRepository",
    "ChatRepository",
    "PostRepository",
    "StoryRepository",
    "SendPostRequestRepository",
    "PublishStoryRequestRepository",
    "StoryToPublishRepository",
    "PostToPublishRepository",
    "WorkerMessageRepository",
    "ProxyRepository",
    "MainDBSettings",
    "apply_migrations",
    "NoFreeProxiesException",
]

session_maker = None


def get_sessionmaker():
    return session_maker


def init_db(url: str):
    global session_maker

    engine = create_async_engine(
        url,
        echo=False,
        pool_recycle=1800,
        pool_timeout=30,
    )

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
