from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from shared.settings import AbstractSettings, JwtSettings, EnvironmentSettings, BotSettings
from shared.infrastructure.main_db import MainDBSettings

from user_bot.settings import ServiceAccountSettings


class Settings(AbstractSettings):
    db: MainDBSettings = Field(default_factory=MainDBSettings)
    jwt: JwtSettings
    environment: EnvironmentSettings
    bot: BotSettings = Field(default_factory=BotSettings)
    service_account: ServiceAccountSettings

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent / "settings.json",
        json_file_encoding="utf-8",
    )

settings = Settings()
