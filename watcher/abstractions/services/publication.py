from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.domain.models import Publication, SendingRequest
from shared.domain.requests import PublicationType, PublicationStartedRequest


class PublicationServiceInterface(ABC):
    @abstractmethod
    async def register_finished_request(self, request: SendingRequest) -> None:
        ...
