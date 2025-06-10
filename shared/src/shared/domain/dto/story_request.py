from datetime import datetime
from typing import Optional
from uuid import UUID

from .abstract import CreateDTO, UpdateDTO
from shared.domain.enums import SendPostRequestStatus, PublishStoryRequestStatus


class CreatePublishStoryRequestDTO(CreateDTO):
    story_id: UUID
    user_id: UUID
    scheduled_at: Optional[datetime] = None

    publication_id: UUID

    status: PublishStoryRequestStatus
    published_at: Optional[datetime] = None


class UpdatePublishStoryRequestDTO(UpdateDTO):
    story_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    publication_id: Optional[UUID] = None
    status: Optional[PublishStoryRequestStatus] = None
    published_at: Optional[datetime] = None
