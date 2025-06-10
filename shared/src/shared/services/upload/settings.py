from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from shared.settings import AbstractSettings


class UploadSettings(AbstractSettings):
    host_upload_dir: str = Field('/Users/daria/Downloads/ai_assistant 4/upload/')
    app_upload_dir: str = Field('/app/upload/')

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent.parent.parent / "upload_settings.json",
        json_file_encoding="utf-8",
        populate_by_name=True,
    )
