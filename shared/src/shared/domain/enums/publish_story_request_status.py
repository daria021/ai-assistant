from enum import StrEnum


class PublishStoryRequestStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
