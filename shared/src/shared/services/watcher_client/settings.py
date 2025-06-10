from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from shared.settings import AbstractSettings


class WatcherSettings(AbstractSettings):
    host: str = Field('watcher')
    port: int = Field(8080)

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent.parent / "watcher_settings.json",
        json_file_encoding="utf-8",
        populate_by_name=True,
    )
