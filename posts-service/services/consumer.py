import logging
from asyncio import sleep
from dataclasses import dataclass
from typing import NoReturn

from shared.abstractions.repositories import PostToPublishRepositoryInterface
from shared.domain.enums import PublicationStatus

from abstractions.services.cosumer import PostsConsumerInterface
from abstractions.services.posting import PostingServiceInterface

logger = logging.getLogger(__name__)


@dataclass
class PostsConsumer(PostsConsumerInterface):
    posting_service: PostingServiceInterface

    posts_to_publish_repository: PostToPublishRepositoryInterface

    idle_delay: int = 10
    global_delay: int = 10

    async def execute(self) -> NoReturn:
        logger.info("Consumer started")
        while True:
            post_to_publish = await self.posts_to_publish_repository.get_queued_post()
            if not post_to_publish:
                logger.info("No posts to publish")
                await sleep(self.idle_delay)
                continue

            logger.info("Scheduling post")
            await self.posts_to_publish_repository.set_status(
                post_id=post_to_publish.id,
                status=PublicationStatus.SCHEDULING,
            )
            try:
                await self.posting_service.schedule_post(post_to_publish)
            except Exception as e:
                logger.error(f"Failed to schedule post: {e}", exc_info=True)
                await self.posts_to_publish_repository.set_status(
                    post_id=post_to_publish.id,
                    status=PublicationStatus.FAILED,
                )
            else:
                logger.info("Post scheduled successfully")
                await self.posts_to_publish_repository.set_status(
                    post_id=post_to_publish.id,
                    status=PublicationStatus.SCHEDULED,
                )

            await sleep(self.global_delay)
