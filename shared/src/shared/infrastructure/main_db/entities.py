from datetime import datetime, time, date
from typing import Optional
from uuid import UUID as pyUUID

from sqlalchemy import ForeignKey, UUID, Enum, func, BigInteger, Table, Column
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.domain.enums import (
    UserRole,
    SendPostRequestStatus,
    PublishStoryRequestStatus,
    WorkerMessageType,
    WorkerMessageStatus, ScheduledType, PublicationStatus,
)

Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )


class User(AbstractBase):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    telegram_username: Mapped[Optional[str]]
    telegram_first_name: Mapped[Optional[str]]
    telegram_last_name: Mapped[Optional[str]]
    telegram_language_code: Mapped[Optional[str]]

    role: Mapped[UserRole] = mapped_column(Enum(UserRole))

    session_string: Mapped[Optional[str]]
    proxy_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('proxies.id'), unique=True)

    assistant_enabled: Mapped[bool] = mapped_column(default=False)

    proxy: Mapped[Optional['Proxy']] = relationship('Proxy')


class Proxy(AbstractBase):
    __tablename__ = "proxies"

    proxy_string: Mapped[str] = mapped_column(unique=True)
    is_free: Mapped[bool] = mapped_column(default=True)
    is_deprecated: Mapped[bool] = mapped_column(default=False)

    user: Mapped[User] = relationship('User')


class Chat(AbstractBase):
    __tablename__ = "chats"

    name: Mapped[str]
    invite_link: Mapped[Optional[str]]
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)


class Post(AbstractBase):
    __tablename__ = "posts"

    name: Mapped[str]
    text: Mapped[str]
    image_path: Mapped[Optional[str]]

    html: Mapped[Optional[str]]
    entities: Mapped[Optional[list[dict]]] = mapped_column(JSONB)


post_to_publish_chat_association = Table(
    "post_to_publish_chat_association",
    AbstractBase.metadata,
    Column("post_to_publish_id", ForeignKey("posts_to_publish.id"), primary_key=True),
    Column("chat_id", ForeignKey("chats.id"), primary_key=True),
)


class PostToPublish(AbstractBase):
    __tablename__ = "posts_to_publish"

    post_id: Mapped[pyUUID] = mapped_column(ForeignKey("posts.id"))
    manager_id: Mapped[pyUUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True)
    scheduled_type: Mapped[ScheduledType]
    scheduled_date: Mapped[Optional[date]]
    scheduled_time: Mapped[time]
    status: Mapped[PublicationStatus]

    manager: Mapped[User] = relationship("User", passive_deletes="all")
    post: Mapped[Post] = relationship("Post")
    chats: Mapped[list[Chat]] = relationship("Chat", secondary=post_to_publish_chat_association)


class SendPostRequest(AbstractBase):
    __tablename__ = "send_post_requests"

    post_id: Mapped[pyUUID] = mapped_column(ForeignKey("posts.id"))
    chat_id: Mapped[pyUUID] = mapped_column(ForeignKey("chats.id"))
    user_id: Mapped[pyUUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True)
    scheduled_at: Mapped[Optional[datetime]]

    publication_id: Mapped[pyUUID] = mapped_column(ForeignKey("posts_to_publish.id"))

    status: Mapped[SendPostRequestStatus] = mapped_column(Enum(SendPostRequestStatus))
    sent_at: Mapped[Optional[datetime]]

    user: Mapped["User"] = relationship("User", passive_deletes="all")
    chat: Mapped["Chat"] = relationship("Chat")
    post: Mapped["Post"] = relationship("Post")


class Story(AbstractBase):
    __tablename__ = 'stories'

    name: Mapped[str]
    file_path: Mapped[str]
    text: Mapped[Optional[str]]


class StoryToPublish(AbstractBase):
    __tablename__ = 'stories_to_publish'

    story_id: Mapped[pyUUID] = mapped_column(ForeignKey("stories.id"))
    manager_id: Mapped[pyUUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    scheduled_type: Mapped[ScheduledType]
    scheduled_date: Mapped[date]
    scheduled_time: Mapped[time]
    status: Mapped[PublicationStatus]

    manager: Mapped["User"] = relationship("User", passive_deletes="all")
    story: Mapped["Story"] = relationship("Story")


class PublishStoryRequest(AbstractBase):
    __tablename__ = "publish_story_requests"

    story_id: Mapped[pyUUID] = mapped_column(ForeignKey("stories.id"))
    user_id: Mapped[pyUUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    scheduled_at: Mapped[Optional[datetime]]

    publication_id: Mapped[pyUUID] = mapped_column(ForeignKey("stories_to_publish.id"))

    status: Mapped[PublishStoryRequestStatus] = mapped_column(Enum(PublishStoryRequestStatus))
    published_at: Mapped[Optional[datetime]]

    user: Mapped["User"] = relationship("User", passive_deletes="all")
    story: Mapped["Story"] = relationship("Story")


class Emoji(AbstractBase):
    __tablename__ = "emojis"

    name: Mapped[str]
    custom_emoji_id: Mapped[str]
    img_url: Mapped[str]


# internal workers data
class WorkerMessage(AbstractBase):
    __tablename__ = "worker_messages"

    user_id: Mapped[Optional[pyUUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    type: Mapped[WorkerMessageType] = mapped_column(Enum(WorkerMessageType))
    text: Mapped[Optional[str]]
    entities: Mapped[Optional[list[dict]]] = mapped_column(JSONB)
    media_path: Mapped[Optional[str]]

    request_id: Mapped[Optional[pyUUID]] = mapped_column(UUID(as_uuid=True))

    status: Mapped[WorkerMessageStatus] = mapped_column(Enum(WorkerMessageStatus))
    sent_at: Mapped[Optional[datetime]]

    user: Mapped["User"] = relationship("User", passive_deletes="all")
