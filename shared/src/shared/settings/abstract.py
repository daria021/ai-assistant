from pathlib import Path
from typing import Type

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)

from .merged_source import MergedSettingsSource


class AbstractSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent / "settings.json",
        json_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            MergedSettingsSource(
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            ),
        )
