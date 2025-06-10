from pydantic import Field
from pydantic_settings import BaseSettings


class MiniappSettings(BaseSettings):
    url: str = Field(..., alias="MINIAPP_URL")
