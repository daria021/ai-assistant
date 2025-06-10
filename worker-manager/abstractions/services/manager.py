from abc import ABC, abstractmethod

from shared.domain.models import SendingRequest

class AccountManagerInterface(ABC):
    @abstractmethod
    async def send(self, request: SendingRequest):
        ...
