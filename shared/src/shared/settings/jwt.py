from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
)


class JwtSettings(BaseSettings):
    secret_key: SecretStr
    issuer: str
    audience: str
    access_expire: int = 60 * 15 * 100  # todo
    refresh_expire: int = 60 * 60 * 24 * 90
    allowed_origins: list[str]
