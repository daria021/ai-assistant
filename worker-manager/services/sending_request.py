import logging
from dataclasses import dataclass
from typing import Optional

from shared.abstractions.repositories import SendPostRequestRepositoryInterface
from shared.domain.dto import UpdateSendPostRequestDTO
from shared.domain.enums import SendPostRequestStatus
from shared.domain.models import SendingRequest, SendPostRequest

from abstractions.services.sending_request import SendingRequestServiceInterface

logger = logging.getLogger(__name__)


@dataclass
class SendingRequestService(SendingRequestServiceInterface):
    post_request_repository: SendPostRequestRepositoryInterface

    async def get_queued_message(self) -> Optional[SendingRequest]:
        message = await self.post_request_repository.get_queued_message()
        logger.info(f"Received message {message}")
        return message

    async def set_in_progress(self, request: SendingRequest):
        if isinstance(request, SendPostRequest):
            dto = UpdateSendPostRequestDTO(
                status=SendPostRequestStatus.IN_PROGRESS,
            )

            await self.post_request_repository.update(
                obj_id=request.id,
                obj=dto,
            )

    async def set_failed(self, request: SendingRequest) -> None:
        if isinstance(request, SendPostRequest):
            dto = UpdateSendPostRequestDTO(
                status=SendPostRequestStatus.FAILED,
            )

            await self.post_request_repository.update(
                obj_id=request.id,
                obj=dto,
            )
