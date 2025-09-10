from abc import ABC, abstractmethod

from shared.domain.requests import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest, RequestStatusChangedRequest


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

    @abstractmethod
    async def report_request_status_changed(self, request: RequestStatusChangedRequest) -> None:
        ...
