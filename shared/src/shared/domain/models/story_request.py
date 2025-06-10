from datetime import datetime
from typing import Optional
from uuid import UUID

from shared.domain.enums import PublishStoryRequestStatus
from .abstract import Model
from .story import Story
from .user import User


class PublishStoryRequest(Model):
    story_id: UUID
    user_id: UUID
    scheduled_at: Optional[datetime] = None

    publication_id: UUID

    status: PublishStoryRequestStatus
    published_at: Optional[datetime] = None

    user: Optional["User"] = None
    story: Optional["Story"] = None
