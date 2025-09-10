from pathlib import Path
from uuid import UUID

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.infrastructure.main_db import MainDBSettings
from shared.services.watcher_client import WatcherSettings
from shared.settings import AbstractSettings
from shared.settings.scheduler import SchedulerSettings

class SenderSettings(AbstractSettings):
    id: UUID = Field(..., alias="SENDER_MANAGER_ID")


class BootstrapSettings(AbstractSettings):
    # How many minutes past the scheduled time a SINGLE post is allowed to be
    # before being considered stale during bootstrap restore.
    single_miss_grace_minutes: int = Field(default=60)


class Settings(AbstractSettings):
    db: MainDBSettings = Field(default_factory=MainDBSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    watcher: WatcherSettings = Field(default_factory=WatcherSettings)
    sender: SenderSettings
    bootstrap: BootstrapSettings = Field(default_factory=BootstrapSettings)

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent / "settings.json",
        json_file_encoding="utf-8",
    )


settings = Settings()
