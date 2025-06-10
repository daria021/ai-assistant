from datetime import datetime
from typing import Optional
from uuid import UUID

from shared.domain.models import User, Post, Chat
from shared.domain.enums import SendPostRequestStatus
from .abstract import Model


class SendPostRequest(Model):
    post_id: UUID
    chat_id: UUID
    user_id: UUID
    scheduled_at: Optional[datetime] = None

    publication_id: UUID

    status: SendPostRequestStatus
    sent_at: Optional[datetime] = None

    user: Optional["User"] = None
    chat: Optional["Chat"] = None
    post: Optional["Post"] = None
