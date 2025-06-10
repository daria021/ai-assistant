from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.domain.models import WorkerMessage, SendingRequest
from shared.domain.requests import PublicationType, RequestProcessingStartedRequest


class SendingRequestsServiceInterface(ABC):
    @abstractmethod
    async def get_request(self, request_id: UUID, request_type: PublicationType) -> Optional[SendingRequest]:
        ...

    @abstractmethod
    async def register_sent_message(self, message: WorkerMessage) -> None:
        ...
