from datetime import date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared.domain.enums import ScheduledType, PublicationStatus
from .abstract import CreateDTO, UpdateDTO


class MessageEntityDTO(BaseModel):
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    custom_emoji_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CreatePostToPublishDTO(CreateDTO):
    post_id: UUID
    creator_id: Optional[UUID] = None
    responsible_manager_id: UUID
    scheduled_type: ScheduledType
    scheduled_date: Optional[date] = None
    scheduled_time: time
    chat_ids: list[UUID]
    status: PublicationStatus


class UpdatePostToPublishDTO(UpdateDTO):
    post_id: Optional[UUID] = None
    creator_id: Optional[UUID] = None
    responsible_manager_id: Optional[UUID] = None
    scheduled_type: Optional[ScheduledType] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    chat_ids: Optional[list[UUID]] = None
    status: Optional[PublicationStatus] = None
