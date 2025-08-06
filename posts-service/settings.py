from pathlib import Path
from uuid import UUID

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.infrastructure.main_db import MainDBSettings
from shared.services.watcher_client import WatcherSettings
from shared.settings import AbstractSettings
from shared.settings.scheduler import SchedulerSettings


class Settings(AbstractSettings):
    db: MainDBSettings = Field(default_factory=MainDBSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    watcher: WatcherSettings = Field(default_factory=WatcherSettings)
    sender_id: UUID = Field(alias="SENDER_MANAGER_ID")

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent / "settings.json",
        json_file_encoding="utf-8",
    )


settings = Settings()
