from datetime import date, time
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict

from shared.domain.enums import ScheduledType, PublicationStatus
from .abstract import Model
from .chat import Chat
from .post import Post
from .user import User


class PostToPublish(Model):
    post_id: UUID
    creator_id: UUID
    responsible_manager_id: UUID
    scheduled_type: ScheduledType
    scheduled_date: Optional[date]
    scheduled_time: time
    status: PublicationStatus

    creator: User
    responsible_manager: User
    chats: list[Chat] = []
    post: Post

    model_config = ConfigDict(from_attributes=True)
