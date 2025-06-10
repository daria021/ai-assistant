from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.domain.models import WorkerMessage
from shared.domain.requests import MessageSentRequest


class MessageServiceInterface(ABC):
    @abstractmethod
    async def get_message(self, message_id: UUID) -> Optional[WorkerMessage]:
        ...

    @abstractmethod
    async def register_message(self, request: MessageSentRequest) -> None:
        ...
