import logging
from urllib.parse import urljoin

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class EnvironmentSettings(BaseSettings):
    env_name: str = Field('local', alias='ENVIRONMENT')
    host: str = Field('localhost:9090', alias='APP_HOST')

    @property
    def api_host(self) -> str:
        host = self.host
        if not host.endswith('/'):
            host += '/'

        logger.info('making api host')
        logger.info(f'host: {host}')
        result = urljoin(host, 'api')
        logger.info(f'result: {result}')
        return result

    @property
    def is_debug(self) -> bool:
        return self.env_name in ('development', 'local')

    @property
    def is_safe(self) -> bool:
        return self.env_name in ('local',)
