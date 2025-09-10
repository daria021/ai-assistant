from dataclasses import dataclass

from shared.abstractions.repositories import PostToPublishRepositoryInterface, SendPostRequestRepositoryInterface
from shared.domain.dto import UpdatePostToPublishDTO
from shared.domain.enums import SendPostRequestStatus, PublicationStatus
from shared.domain.models import SendingRequest, SendPostRequest

from abstractions.services.publication import PublicationServiceInterface


@dataclass
class PublicationService(PublicationServiceInterface):
    post_to_publish_repository: PostToPublishRepositoryInterface
    posts_request_repository: SendPostRequestRepositoryInterface

    async def register_finished_request(self, request: SendingRequest) -> None:
        if not isinstance(request, SendPostRequest):
            return

        requests = await self.posts_request_repository.get_requests_from_same_publication(request.id)
        statuses = {r.status for r in requests}

        # Case 1: all sent -> POSTED (existing behavior)
        if statuses and statuses.issubset({SendPostRequestStatus.SENT}):
            await self.post_to_publish_repository.update(
                obj_id=request.publication_id,
                obj=UpdatePostToPublishDTO(status=PublicationStatus.POSTED),
            )
            return

        # Case 2: all terminal (no PLANNED or IN_PROGRESS)
        if not (SendPostRequestStatus.PLANNED in statuses or SendPostRequestStatus.IN_PROGRESS in statuses):
            # If any were SENT and others failed/stale -> FAILED
            if SendPostRequestStatus.SENT in statuses:
                await self.post_to_publish_repository.update(
                    obj_id=request.publication_id,
                    obj=UpdatePostToPublishDTO(status=PublicationStatus.FAILED),
                )
                return

            # If none SENT and all terminal non-sent -> STALE (e.g., all FAILED/STALE)
            if statuses.issubset({SendPostRequestStatus.FAILED, SendPostRequestStatus.STALE}):
                await self.post_to_publish_repository.update(
                    obj_id=request.publication_id,
                    obj=UpdatePostToPublishDTO(status=PublicationStatus.STALE),
                )
                return

        # todo: stories
