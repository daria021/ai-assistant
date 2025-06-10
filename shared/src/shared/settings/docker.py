from pydantic import Field
from pydantic_settings import BaseSettings


class DockerSettings(BaseSettings):
    workers_network_name: str
    app_root_config_path: str
    host_root_config_path: str = Field(..., alias='HOST_ROOT_CONFIG_PATH')
    worker_image: str
