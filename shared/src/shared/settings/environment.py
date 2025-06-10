from pydantic import Field
from pydantic_settings import BaseSettings


class EnvironmentSettings(BaseSettings):
    env_name: str = Field('local', alias='ENVIRONMENT')
    host: str = Field('localhost:8080', alias='APP_HOST')

    @property
    def is_debug(self) -> bool:
        return self.env_name in ('development', 'local')

    @property
    def is_safe(self) -> bool:
        return self.env_name in ('local',)
