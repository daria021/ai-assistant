from abc import ABC, abstractmethod

from shared.domain.requests import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest


class WatcherClientInterface(ABC):
    @abstractmethod
    async def report_publication_started(self, request: PublicationStartedRequest) -> None:
        ...

    @abstractmethod
    async def report_request_processing_started(self, request: RequestProcessingStartedRequest) -> None:
        ...

    @abstractmethod
    async def report_message_sent(self, request: MessageSentRequest) -> None:
        ...
