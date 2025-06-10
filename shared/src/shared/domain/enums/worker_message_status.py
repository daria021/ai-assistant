from enum import StrEnum

class WorkerMessageStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SENT = "sent"
    FAILED = "failed"
