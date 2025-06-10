from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from shared.domain.models import UserWithSessionString


@dataclass
class WorkerContainer:
    id: UUID
    config_path: Path
    restarts: int = 0
    container_id: str = None


class ContainerManagerInterface(ABC):
    @abstractmethod
    async def get_container(self, worker_id: UUID) -> WorkerContainer:
        pass

    @abstractmethod
    async def start_container(self, worker_id: UUID, config_path: Path) -> None:
        pass

    @abstractmethod
    async def stop_container(self, worker_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_running_containers(self) -> list[WorkerContainer]:
        pass

    @abstractmethod
    async def check_health(self, worker_id: UUID) -> bool:
        pass

    @abstractmethod
    async def repair_container(self, worker_id: UUID) -> bool:
        pass

    @abstractmethod
    async def check_for_active_worker(self, user_id: UUID) -> bool:
        ...

    @abstractmethod
    async def start_watching(self) -> None:
        ...
