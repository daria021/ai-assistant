import logging
from dataclasses import dataclass
from enum import StrEnum

from shared.abstractions.singleton import Singleton
from shared.domain.enums import WorkerMessageStatus
from shared.domain.requests import MessageSentRequest, RequestProcessingStartedRequest, PublicationStartedRequest, RequestStatusChangedRequest

from abstractions.services.messages import MessageServiceInterface
from abstractions.services.publication import PublicationServiceInterface
from abstractions.services.requests import SendingRequestsServiceInterface
from abstractions.services.watcher import WatcherInterface
from services.exceptions import RepeatedRegistrationException

logger = logging.getLogger(__name__)


class ChildEntityStatus(StrEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


@dataclass
class Watcher(
    WatcherInterface,
    Singleton,
):
    publication_service: PublicationServiceInterface
    requests_service: SendingRequestsServiceInterface
    message_service: MessageServiceInterface

    async def register_message(self, request: MessageSentRequest) -> None:
        # if (await self.message_service.get_message(request.message_id)).status == WorkerMessageStatus.SENT:
        #     logger.error(f'Message {request.message_id} already registered')
        #     raise RepeatedRegistrationException(f"Message {request.message_id} already registered.")

        await self.message_service.register_message(request)
        logger.info(f'Message {request.message_id} registered')

    async def register_request_status_change(self, request: RequestStatusChangedRequest) -> None:
        # Re-evaluate the publication status when a child request transitions to a terminal status
        sending_request = await self.requests_service.get_request(request.request_id, self._map_publication_type(request))
        if sending_request:
            await self.publication_service.register_finished_request(sending_request)

    def _map_publication_type(self, request: RequestStatusChangedRequest):
        # Request carries its type already but helper to keep signature explicit
        return request.type
