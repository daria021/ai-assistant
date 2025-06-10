import time
from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.infrastructure.main_db import MainDBSettings
from shared.settings.abstract import AbstractSettings

class TestSettings(AbstractSettings):
    file: str
    main_db: MainDBSettings = Field(default_factory=MainDBSettings)

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent / "settings.json",
        json_file_encoding="utf-8",
    )


settings = TestSettings()

print(settings.main_db.url)
print(settings.file)

time.sleep(10000)