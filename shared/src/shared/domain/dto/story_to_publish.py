from datetime import date, time
from typing import Optional
from uuid import UUID

from shared.domain.enums import ScheduledType, PublicationStatus
from .abstract import UpdateDTO, CreateDTO


class CreateStoryToPublishDTO(CreateDTO):
    story_id: UUID
    manager_id: UUID
    scheduled_type: ScheduledType
    scheduled_date: Optional[date]
    scheduled_time: time
    status: PublicationStatus


class UpdateStoryToPublishDTO(UpdateDTO):
    story_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    scheduled_type: Optional[ScheduledType] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    status: Optional[PublicationStatus] = None
