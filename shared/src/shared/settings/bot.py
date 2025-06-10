from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: SecretStr = Field(..., alias="BOT_TOKEN")
