import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from shared.abstractions.repositories import SendPostRequestRepositoryInterface
from shared.abstractions.repositories.worker_message import WorkerMessageRepositoryInterface
from shared.domain.dto import UpdateSendPostRequestDTO
from shared.domain.enums import WorkerMessageStatus, SendPostRequestStatus, WorkerMessageType
from shared.domain.models import WorkerMessage, SendingRequest
from shared.domain.requests import PublicationType, RequestProcessingStartedRequest

from abstractions.services.publication import PublicationServiceInterface
from abstractions.services.requests import SendingRequestsServiceInterface


logger = logging.getLogger(__name__)


@dataclass
class SendingRequestsService(SendingRequestsServiceInterface):
    post_requests_repository: SendPostRequestRepositoryInterface
    messages_repository: WorkerMessageRepositoryInterface

    publication_service: PublicationServiceInterface

    async def get_request(self, request_id: UUID, request_type: PublicationType) -> Optional[SendingRequest]:
        if request_type == PublicationType.POST:
            return await self.post_requests_repository.get(request_id)

        ...

    async def register_sent_message(self, message: WorkerMessage) -> None:
        messages = await self.messages_repository.get_messages_from_same_request(message.id)
        logger.info(f'messages: {messages}')
        if done := all(map(lambda x: x.status == WorkerMessageStatus.SENT, messages)):
            logger.info(f'done: {done}')
            logger.info(f'type: {message.type}')
            if message.type == WorkerMessageType.POST:
                update_request_dto = UpdateSendPostRequestDTO(
                    status=SendPostRequestStatus.SENT,
                    sent_at=datetime.now(),
                )

                await self.post_requests_repository.update(
                    obj_id=message.request_id,
                    obj=update_request_dto,
                )

                request = await self.get_request(message.request_id, PublicationType.POST)

                await self.publication_service.register_finished_request(request)

            # todo: stories
