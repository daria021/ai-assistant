from abc import ABC, abstractmethod
from typing import Optional

from shared.domain.models import SendingRequest


class SendingRequestServiceInterface(ABC):
    @abstractmethod
    async def get_queued_message(self) -> Optional[SendingRequest]:
        ...

    @abstractmethod
    async def set_in_progress(self, request: SendingRequest) -> None:
        ...

    @abstractmethod
    async def set_failed(self, request: SendingRequest) -> None:
        ...