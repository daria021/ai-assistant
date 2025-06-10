from pydantic import Field
from pydantic_settings import BaseSettings


class MiniappSettings(BaseSettings):
    miniapp_url: str
