import logging
from datetime import datetime
from uuid import UUID

from shared.dependencies.repositories import get_post_request_repository
from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository
from shared.domain.dto import CreateSendPostRequestDTO
from shared.domain.enums import SendPostRequestStatus, PublicationStatus
# from shared.domain.requests import PostPublicationStartedRequest

# from dependencies.services.watcher_client import get_watcher_client
from settings import settings


async def publish(post_id: UUID) -> None:
    posts_to_publish_repository = get_post_to_publish_repository()
    post_requests_repository = get_post_request_repository()
    # watcher_client = get_watcher_client()

    logger = logging.getLogger(f'publisher_job_{post_id}')

    post = await posts_to_publish_repository.get(post_id)

    if post.deleted_at is not None:
        logger.info(f"Publishing of post {post.id} is cancelled due to the post deletion")
        await posts_to_publish_repository.set_status(post.id, PublicationStatus.CANCELED)
        return

    logger.info(f"Publishing post {post.id}")
    # Mark publication as in progress
    try:
        await posts_to_publish_repository.set_status(post.id, PublicationStatus.IN_PROGRESS)
    except Exception:
        logger.error("Failed to set publication status to IN_PROGRESS", exc_info=True)

    try:
        child_requests: list[UUID] = []
        for chat in post.chats:
            post_request_dto = CreateSendPostRequestDTO(
                post_id=post.post_id,
                chat_id=chat.id,
                user_id=settings.sender.id,
                status=SendPostRequestStatus.PLANNED,
                publication_id=post.id,
                scheduled_at=(
                    datetime.combine(post.scheduled_date, post.scheduled_time)
                    if post.scheduled_date is not None else datetime.now()
                ),
            )

            new = await post_requests_repository.create(post_request_dto)
            child_requests.append(new)

    except Exception as e:
        logger.error(f"Failed to publish post: {e}", exc_info=True)
        try:
            await posts_to_publish_repository.set_status(post.id, PublicationStatus.FAILED)
        except Exception:
            logger.error("Failed to set publication status to FAILED", exc_info=True)
