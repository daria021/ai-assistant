from datetime import datetime
from typing import Optional
from uuid import UUID

from shared.domain.dto.abstract import CreateDTO, UpdateDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.enums import WorkerMessageType, WorkerMessageStatus


class CreateWorkerMessageDTO(CreateDTO):
    user_id: UUID
    chat_id: int
    type: WorkerMessageType
    text: Optional[str] = None
    media_path: Optional[str] = None
    status: WorkerMessageStatus
    sent_at: Optional[datetime] = None

    request_id: Optional[UUID] = None

    entities: Optional[list[MessageEntityDTO]] = None


class UpdateWorkerMessageDTO(UpdateDTO):
    user_id: Optional[UUID] = None
    chat_id: Optional[int] = None
    type: Optional[WorkerMessageType] = None
    text: Optional[str] = None
    media_path: Optional[str] = None
    status: Optional[WorkerMessageStatus] = None
    sent_at: Optional[datetime] = None

    request_id: Optional[UUID] = None

    entities: Optional[list[MessageEntityDTO]] = None
