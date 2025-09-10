from datetime import datetime
from typing import Optional
from uuid import UUID

from .abstract import CreateDTO, UpdateDTO
from shared.domain.enums import SendPostRequestStatus


class CreateSendPostRequestDTO(CreateDTO):
    post_id: UUID
    chat_id: UUID
    user_id: UUID
    scheduled_at: Optional[datetime] = None
    publication_id: UUID
    status: SendPostRequestStatus
    sent_at: Optional[datetime] = None
    stale_at: Optional[datetime] = None


class UpdateSendPostRequestDTO(UpdateDTO):
    post_id: Optional[UUID] = None
    chat_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    publication_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[SendPostRequestStatus] = None
    sent_at: Optional[datetime] = None
    stale_at: Optional[datetime] = None
