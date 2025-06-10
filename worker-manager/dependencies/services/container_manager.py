from pathlib import Path

from abstractions.services.container_manager import ContainerManagerInterface
from infrastructure.docker import AsyncDockerAPIRepository
from user_bot.settings import settings


def get_container_manager() -> ContainerManagerInterface:
    return AsyncDockerAPIRepository(
        host_root_config_path=Path(settings.docker.host_root_config_path),
        host_upload_dir=Path(settings.upload.host_upload_dir),
        app_upload_dir=Path(settings.upload.app_upload_dir),

        network_name=settings.docker.workers_network_name,
        worker_image=settings.docker.worker_image,
    )
