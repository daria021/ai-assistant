from datetime import datetime
from typing import Optional
from uuid import UUID

from infrastructure.enums.story_status import StoryStatus
from domain.dto.base import CreateDTO, UpdateDTO
from domain.models.user import User


class CreateStoryDTO(CreateDTO):
    manager_id: UUID
    file_path: str
    scheduled_time: datetime
    status: StoryStatus

class UpdateStoryDTO(UpdateDTO):
    manager_id: Optional[UUID]
    file_path: Optional[str]
    scheduled_time: Optional[datetime]
    status: Optional[StoryStatus]
