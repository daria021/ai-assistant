from abc import ABC, abstractmethod

from shared.domain.requests import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest


class WatcherInterface(
    ABC,
):
    @abstractmethod
    async def register_message(self, request: MessageSentRequest) -> None:
        ...
