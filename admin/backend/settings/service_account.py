from typing import Optional

from pydantic import SecretStr, Field
from shared.settings import AbstractSettings


class ServiceAccountSettings(AbstractSettings):
    api_id: int
    api_hash: str
    session_string: SecretStr = Field(..., alias="SA_SESSION_STRING")
    proxy: Optional[str] = None
    service_bot_token: SecretStr = Field(..., alias="SERVICE_BOT_TOKEN")
    use_bot_for_service: bool = False
