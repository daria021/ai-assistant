from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from .abstract import AbstractSettings


class DBSettings(AbstractSettings):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr

    model_config = SettingsConfigDict(populate_by_name=True, extra="forbid")

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )
