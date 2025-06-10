from datetime import date, time
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict

from shared.domain.enums import ScheduledType, PublicationStatus
from .user import User
from .abstract import Model
from .story import Story


class StoryToPublish(Model):
    story_id: UUID
    manager_id: UUID
    scheduled_type: ScheduledType
    scheduled_date: Optional[date]
    scheduled_time: time
    status: PublicationStatus

    manager: User
    story: Story

    model_config = ConfigDict(from_attributes=True)
