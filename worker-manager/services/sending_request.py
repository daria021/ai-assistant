import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

from shared.abstractions.repositories import SendPostRequestRepositoryInterface
from shared.domain.dto import UpdateSendPostRequestDTO
from shared.domain.enums import SendPostRequestStatus
from shared.domain.requests import PostRequestStatusChangedRequest
from shared.domain.models import SendingRequest, SendPostRequest

from abstractions.services.sending_request import SendingRequestServiceInterface
from shared.abstractions.services.watcher_client import WatcherClientInterface

logger = logging.getLogger(__name__)


@dataclass
class SendingRequestService(SendingRequestServiceInterface):
    post_request_repository: SendPostRequestRepositoryInterface
    stale_threshold: timedelta = timedelta(hours=1)
    watcher_client: WatcherClientInterface | None = None

    async def get_queued_message(self) -> Optional[SendingRequest]:
        
        # Defense-in-depth: drop stale queued requests (older than 1 hour)
        # Context: send post requests are created at the intended send time (MSK).
        # If services were down, very old PLANNED requests could flood out later.
        # We mark such requests as FAILED and skip them.
        stale_threshold = self.stale_threshold

        while True:
            message = await self.post_request_repository.get_queued_message()
            if message is None:
                return None

            try:
                now = datetime.now()  # created_at is stored without tz (DB/MSK)
                if (now - message.created_at) > stale_threshold:
                    age = now - message.created_at
                    logger.warning(
                        "Marking request %s as STALE at %s (age=%s > %s)",
                        getattr(message, 'id', None),
                        now.isoformat(),
                        age,
                        stale_threshold,
                    )
                    await self.set_stale(message)
                    # Continue to check next queued message
                    continue
            except Exception:
                # If comparison fails for any reason, fall back to returning the message
                logger.error("Failed to evaluate staleness for message %s", getattr(message, 'id', None), exc_info=True)
                return message

            logger.info(f"Received message {message}")
            return message

    async def set_stale(self, request: SendingRequest) -> None:
        if isinstance(request, SendPostRequest):
            dto = UpdateSendPostRequestDTO(
                status=SendPostRequestStatus.STALE,
                stale_at=datetime.now(),
            )

            await self.post_request_repository.update(
                obj_id=request.id,
                obj=dto,
            )
            # Notify watcher that a child request became terminal to allow publication finalization
            if self.watcher_client:
                await self.watcher_client.report_request_status_changed(
                    PostRequestStatusChangedRequest(request_id=request.id)
                )

    async def set_in_progress(self, request: SendingRequest):
        if isinstance(request, SendPostRequest):
            dto = UpdateSendPostRequestDTO(
                status=SendPostRequestStatus.IN_PROGRESS,
            )

            await self.post_request_repository.update(
                obj_id=request.id,
                obj=dto,
            )
            if self.watcher_client:
                await self.watcher_client.report_request_status_changed(
                    PostRequestStatusChangedRequest(request_id=request.id)
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
