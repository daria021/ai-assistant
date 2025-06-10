from pathlib import Path

from pydantic import Field

from pydantic_settings import SettingsConfigDict

from shared.infrastructure.main_db import MainDBSettings
from shared.settings import AbstractSettings


class Settings(AbstractSettings):
    db: MainDBSettings = Field(default_factory=MainDBSettings)

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent / "settings.json",
        json_file_encoding="utf-8",
    )

settings = Settings()
