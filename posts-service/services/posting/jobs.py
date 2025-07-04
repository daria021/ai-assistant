import logging
from uuid import UUID

from shared.dependencies.repositories import get_post_request_repository
from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository
from shared.domain.dto import CreateSendPostRequestDTO
from shared.domain.enums import SendPostRequestStatus
from shared.domain.requests import PostPublicationStartedRequest

from dependencies.services.watcher_client import get_watcher_client


async def publish(post_id: UUID) -> None:
    posts_to_publish_repository = get_post_to_publish_repository()
    post_requests_repository = get_post_request_repository()
    watcher_client = get_watcher_client()

    logger = logging.getLogger(f'publisher_job_{post_id}')

    post = await posts_to_publish_repository.get(post_id)

    logger.info(f"Publishing post {post.id}")

    try:
        child_requests: list[UUID] = []
        for chat in post.chats:
            logger.info(f"создание CreateSendPostRequestDTO")
            post_request_dto = CreateSendPostRequestDTO(
                post_id=post.post_id,
                chat_id=chat.id,
                user_id=post.responsible_manager_id,
                status=SendPostRequestStatus.PLANNED,
                publication_id=post.id,
            )

            new = await post_requests_repository.create(post_request_dto)
            logger.info(f"Post request created: {new}")
            child_requests.append(new)

    except Exception as e:
        logger.error(f"Failed to publish post: {e}", exc_info=True)
