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
        """
        Returns a fully-qualified base URL for backend API, ensuring:
        - Scheme is present (defaults to https if missing)
        - Single `/api` prefix appended (does not duplicate if already present)
        - No trailing slash guaranteed (consistent with callers building paths)
        """
        host = (self.host or '').strip()

        # Ensure scheme
        if not (host.startswith('http://') or host.startswith('https://')):
            host = f'https://{host}'

        # Ensure trailing slash for urljoin behavior
        if not host.endswith('/'):
            host += '/'

        # Join with `api` (urljoin with a relative path avoids duplicating when base already ends with `api/`)
        api_base = urljoin(host, 'api')

        # Normalize: drop trailing slash for consistency
        if api_base.endswith('/'):
            api_base = api_base[:-1]

        return api_base

    @property
    def is_debug(self) -> bool:
        return self.env_name in ('development', 'local')

    @property
    def is_safe(self) -> bool:
        return self.env_name in ('local',)
