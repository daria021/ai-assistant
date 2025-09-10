from enum import StrEnum


class PublicationStatus(StrEnum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SCHEDULING = "scheduling"
    IN_PROGRESS = "in_progress"
    POSTED = "posted"
    FAILED = "failed"
    CANCELED = "canceled"
    STALE = "stale"
