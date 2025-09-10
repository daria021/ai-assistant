from abc import ABC, abstractmethod

from shared.domain.requests import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest, RequestStatusChangedRequest


class WatcherInterface(
    ABC,
):
    @abstractmethod
    async def register_message(self, request: MessageSentRequest) -> None:
        ...

    @abstractmethod
    async def register_request_status_change(self, request: RequestStatusChangedRequest) -> None:
        ...
