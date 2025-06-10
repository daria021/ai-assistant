from abc import ABC, abstractmethod

from shared.domain.models import WorkerMessage


class SenderInterface(ABC):
    @abstractmethod
    async def send(self, message: WorkerMessage):
        ...
