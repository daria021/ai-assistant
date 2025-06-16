from pydantic import SecretStr, Field
from shared.settings import BotSettings


class PostingBotSettings(BotSettings):
    token: SecretStr = Field(..., alias="POSTING_BOT_TOKEN")
    username: str = Field(..., alias="POSTING_BOT_USERNAME")
