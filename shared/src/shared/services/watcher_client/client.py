from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from httpx import AsyncClient
from pydantic import BaseModel

from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.domain.requests import MessageSentRequest, RequestProcessingStartedRequest, PublicationStartedRequest


@dataclass
class WatcherClient(WatcherClientInterface):
    base_url: str

    publication_started_endpoint: str = "/watch/publication"
    request_processing_started_endpoint: str = "/watch/request"
    message_sent_endpoint: str = "/watch/message"

    async def report_publication_started(self, request: PublicationStartedRequest) -> None:
        await self._send_post_request(
            request=request,
            endpoint=self.publication_started_endpoint,
        )

    async def report_request_processing_started(self, request: RequestProcessingStartedRequest) -> None:
        await self._send_post_request(
            request=request,
            endpoint=self.request_processing_started_endpoint,
        )

    async def report_message_sent(self, request: MessageSentRequest) -> None:
        await self._send_post_request(
            request=request,
            endpoint=self.message_sent_endpoint,
        )

    async def _send_post_request(self, request: BaseModel, endpoint: str) -> None:
        async with self._get_client() as client:
            await client.post(
                url=endpoint,
                json=request.model_dump(mode="json"),
            )

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[AsyncClient, None]:
        async with AsyncClient(base_url=self.base_url) as client:
            yield client
