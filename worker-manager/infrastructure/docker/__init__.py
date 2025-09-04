from asyncio import sleep
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import Any
from uuid import UUID

from aiodocker import Docker
from dotenv import dotenv_values
from shared.abstractions.singleton import Singleton

from abstractions.services.container_manager import ContainerManagerInterface, WorkerContainer

logger = getLogger(__name__)


@dataclass
class AsyncDockerAPIRepository(
    ContainerManagerInterface,
    Singleton,
):
    host_root_config_path: Path
    host_upload_dir: Path
    app_upload_dir: Path

    client: Docker = field(default_factory=Docker)

    worker_image: str = 'account-worker'
    network_name: str = "assistant_bridge"
    config_file_destination: Path = Path("/app/settings.json")
    # fluentd_address: str = "localhost:24224"   # todo: logging
    # loki_labels: dict[str, str] = field(default_factory=lambda: {
    #     "service": "worker",
    # })

    max_restarts: int = 3

    _containers: dict[UUID, WorkerContainer] = field(default_factory=dict)

    container_watcher_delay: float = 5

    async def start_watching(self) -> None:
        logger.info(f"Starting container watcher, {id(self)}")
        while True:
            logger.info(f"Refreshing containers!")
            await self.refresh_containers()
            await sleep(self.container_watcher_delay)

    async def check_for_active_worker(self, user_id: UUID) -> bool:
        return user_id in self._containers

    async def get_container(self, worker_id: UUID) -> WorkerContainer:
        return self._containers.get(worker_id)

    async def refresh_containers(self) -> None:
        to_remove = []
        for worker_id, worker in self._containers.items():
            if not await self.check_health(worker_id):
                logger.info(f"Container {worker_id} is not running, clean up...")
                to_remove.append(worker_id)

        for worker_id in to_remove:
            del self._containers[worker_id]

    async def start_container(self, worker_id: UUID, config_path: Path) -> None:
        logger.info(f"Starting container with worker ID {worker_id} and config {config_path}")

        container_name = f"{self.worker_image}-{worker_id}"
        container = await self.client.containers.create_or_replace(
            name=container_name,
            config=self._get_container_config(
                self.worker_image,
                config_path,
                worker_id,
            )
        )
        await container.start()

        # network = await self.client.networks.get(self.network_name)
        # await network.connect({"Container": container.id})

        worker = WorkerContainer(
            id=worker_id,
            config_path=config_path,
            container_id=container.id,
        )

        self._containers[worker_id] = worker

        return container.id

    def _get_container_config(self, image: str, config_path: Path, worker_id: UUID) -> dict[str, Any]:
        env_map = dotenv_values(str('.env'))
        env_list = [f"{k}={v}" for k, v in env_map.items() if v is not None]

        return {
            "Image": image,
            "Env": env_list,
            "HostConfig": {
                "Binds": [
                    f"{self.host_root_config_path / config_path.name}:{self.config_file_destination}:ro",
                    f"{self.host_upload_dir}:{self.app_upload_dir}"
                ],
                # Пример включения docker logging driver (если решим вернуться к fluentd/loki)
                # "LogConfig": {
                #     "Type": "loki",
                #     "Config": {
                #         "loki-url": "http://loki:3100/loki/api/v1/push",
                #         "loki-external-labels": "service=worker,container={{.Name}}"
                #     }
                # },
                "NetworkMode": self.network_name,
            },
        }

    async def stop_container(self, worker_id: UUID) -> None:
        logger.info(f"Stopping container {worker_id}")
        bot = self._containers.pop(worker_id, None)
        if not bot:
            return
        container = await self.client.containers.get(
            container_id=bot.container_id
        )
        await container.delete(force=True)

    async def get_running_containers(self) -> list[WorkerContainer]:
        return list(self._containers.values())

    async def check_health(self, worker_id: UUID) -> bool:
        bot = self._containers.get(worker_id)
        if not bot:
            return False
        container = await self.client.containers.get(
            container_id=bot.container_id
        )
        data = await container.show()
        return data.get("State", {}).get("Running", False)

    async def repair_container(self, worker_id: UUID) -> bool:
        bot = self._containers.get(worker_id)
        if not bot:
            return False
        container = await self.client.containers.get(
            container_id=bot.container_id
        )
        if not await self.check_health(worker_id):
            if bot.restarts >= self.max_restarts:
                return False
            bot.restarts += 1
            await container.restart()
        return True
