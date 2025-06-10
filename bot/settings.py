from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    SettingsConfigDict,
)
from shared.infrastructure.main_db import MainDBSettings
from shared.settings import AbstractSettings, EnvironmentSettings, BotSettings, MiniappSettings


class Settings(AbstractSettings):
    main_db: MainDBSettings = Field(default_factory=MainDBSettings)
    env: EnvironmentSettings = Field(default_factory=EnvironmentSettings)
    bot: BotSettings
    miniapp: MiniappSettings

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent / "settings.json",
        json_file_encoding="utf-8",
    )


settings = Settings()
