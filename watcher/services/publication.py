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
        if isinstance(request, SendPostRequest):
            requests = await self.posts_request_repository.get_requests_from_same_publication(request.id)
            if done := all(map(lambda x: x.status == SendPostRequestStatus.SENT, requests)):
                update_request_dto = UpdatePostToPublishDTO(
                    status=PublicationStatus.POSTED,
                )

                await self.post_to_publish_repository.update(
                    obj_id=request.publication_id,
                    obj=update_request_dto,
                )

        # todo: stories