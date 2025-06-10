from datetime import datetime
from typing import Optional
from uuid import UUID

from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.models import User
from shared.domain.models.abstract import Model
from shared.domain.enums import WorkerMessageType, WorkerMessageStatus


class WorkerMessage(Model):
    user_id: UUID
    type: WorkerMessageType
    text: Optional[str] = None
    media_path: Optional[str] = None
    chat_id: Optional[int] = None
    status: WorkerMessageStatus
    sent_at: Optional[datetime] = None

    request_id: Optional[UUID] = None
    entities: Optional[list[MessageEntityDTO]] = None

    user: Optional[User] = None
