from datetime import datetime
from uuid import UUID

from domain.models.abstract import Model
from domain.models.user import User
from infrastructure.enums.story_status import StoryStatus


class Story(Model):
    manager_id: UUID
    file_path: str
    scheduled_time: datetime
    status: StoryStatus
    manager: User

    model_config = ConfigDict(from_attributes=True)
