from enum import StrEnum


class SendPostRequestStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STALE = "stale"
