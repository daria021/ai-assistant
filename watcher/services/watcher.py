import logging
from dataclasses import dataclass
from enum import StrEnum

from shared.abstractions.singleton import Singleton
from shared.domain.enums import WorkerMessageStatus
from shared.domain.requests import MessageSentRequest, RequestProcessingStartedRequest, PublicationStartedRequest

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
