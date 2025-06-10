from pathlib import Path
from typing import ClassVar

from pydantic import SecretStr, Field
from pydantic_settings import SettingsConfigDict

from shared.settings import DBSettings


class MainDBSettings(DBSettings):
    host: str = Field(..., alias='MAIN_DB_HOST')
    port: int = Field(..., alias='MAIN_DB_PORT')
    name: str = Field(..., alias='MAIN_DB_NAME')
    user: str = Field(..., alias='MAIN_DB_USER')
    password: SecretStr = Field(..., alias='MAIN_DB_PASSWORD')

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent.parent / "settings.json",
        json_file_encoding="utf-8",
        populate_by_name=True,
    )
