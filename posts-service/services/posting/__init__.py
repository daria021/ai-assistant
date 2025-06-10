import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from uuid import UUID

from shared.abstractions.repositories import SendPostRequestRepositoryInterface
from shared.abstractions.services.scheduler import SchedulerInterface
from shared.abstractions.singleton import Singleton
from shared.domain.enums import ScheduledType
from shared.domain.models import PostToPublish

from abstractions.services.posting import PostingServiceInterface
from .jobs import publish

logger = logging.getLogger(__name__)


@dataclass
class PostingService(
    PostingServiceInterface,
    Singleton,
):
    posts_requests_repository: SendPostRequestRepositoryInterface

    scheduler: SchedulerInterface

    async def schedule_post(self, post: PostToPublish):
        match post.scheduled_type:
            case ScheduledType.SINGLE:
                logger.info("Found single scheduled post, scheduling it")
                self._schedule_post(
                    post_id=post.id,
                    schedule_at=datetime.combine(
                        post.scheduled_date,
                        post.scheduled_time,
                    ),
                )
            case ScheduledType.EVERYDAY:
                logger.info("Found daily scheduled post, scheduling it")
                next_run_date = date.today() \
                    if post.scheduled_time > datetime.now().time() \
                    else date.today() + timedelta(days=1)

                self._schedule_post(
                    post_id=post.id,
                    schedule_at=datetime.combine(
                        next_run_date,
                        post.scheduled_time,
                    ),
                )

    def _schedule_post(self, post_id: UUID, schedule_at: datetime) -> None:
        self.scheduler.schedule_once(
            callback=publish,
            runs_on=schedule_at,
            args=(post_id,),
            job_id=f"post_{post_id}",
        )
