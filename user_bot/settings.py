import os
from pathlib import Path
from typing import Type, Tuple, Optional

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    JsonConfigSettingsSource,
)

ENV = os.getenv("ENVIRONMENT", "local")


class DBSettings(BaseSettings):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr

    @property
    def url(self):
        return (
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@"
            f"{self.host}:{self.port}/{self.name}"
        )


class AccountSettings(BaseSettings):
    phone: str
    api_id: int
    api_hash: str
    session_string: Optional[str] = None


class AssistantSettings(BaseSettings):
    openai_api_key: str
    assistant_id: str


class JwtSettings(BaseSettings):
    secret_key: SecretStr
    issuer: str
    audience: str
    access_expire: int
    refresh_expire: int


class BotTokenSettings(BaseSettings):
    token: str
    username: str


class MailingSettings(BaseSettings):
    a_days: str
    b_days: str
    c_days: str
    a_hour: int
    a_minute: int
    b_hour: int
    b_minute: int
    c_hour: int
    c_minute: int



class Settings(BaseSettings):
    db: DBSettings
    jwt: JwtSettings
    account: AccountSettings
    assistant: AssistantSettings
    mailing: MailingSettings

    debug: bool = True

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent / "settings.json",
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
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            JsonConfigSettingsSource(settings_cls),  # Fallback to JSON
        )


settings = Settings()
