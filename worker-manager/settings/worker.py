from pydantic import Field
from shared.settings import AbstractSettings


class CommonWorkerSettings(AbstractSettings):
    api_id: int
    api_hash: str
    # Max age for a queued send request to still be sent (minutes)
    stale_threshold_minutes: int = Field(default=60)
