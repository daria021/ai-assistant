from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from shared.abstractions.repositories import SendPostRequestRepositoryInterface, PostToPublishRepositoryInterface
from shared.abstractions.repositories.worker_message import WorkerMessageRepositoryInterface
from shared.domain.enums import WorkerMessageType, WorkerMessageStatus
from shared.domain.models import WorkerMessage
from shared.domain.requests import MessageSentRequest
from shared.infrastructure.sqlalchemy import NotFoundException

from abstractions.services.messages import MessageServiceInterface
from abstractions.services.requests import SendingRequestsServiceInterface
from services.exceptions import MessageNotFoundException


@dataclass
class MessageService(MessageServiceInterface):
    worker_message_repository: WorkerMessageRepositoryInterface
    post_requests_repository: SendPostRequestRepositoryInterface
    posts_to_publish_repository: PostToPublishRepositoryInterface

    requests_service: SendingRequestsServiceInterface

    async def get_message(self, message_id: UUID) -> Optional[WorkerMessage]:
        try:
            message = await self.worker_message_repository.get(message_id)
            return message
        except NotFoundException:
            return None

    async def register_message(self, request: MessageSentRequest) -> None:
        message = await self.worker_message_repository.get(request.message_id)
        if not message:
            raise MessageNotFoundException

        await self.requests_service.register_sent_message(message)
