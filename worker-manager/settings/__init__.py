from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    SettingsConfigDict,
)
from shared.infrastructure.main_db import MainDBSettings
from shared.services.upload.settings import UploadSettings
from shared.services.watcher_client import WatcherSettings
from shared.settings import AbstractSettings, DockerSettings

from settings import CommonWorkerSettings


class Settings(AbstractSettings):
    db: MainDBSettings = Field(default_factory=MainDBSettings)
    upload: UploadSettings = Field(default_factory=UploadSettings)
    watcher: WatcherSettings = Field(default_factory=WatcherSettings)
    docker: DockerSettings
    worker: CommonWorkerSettings

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent / "settings.json",
        json_file_encoding="utf-8",
    )


settings = Settings()
