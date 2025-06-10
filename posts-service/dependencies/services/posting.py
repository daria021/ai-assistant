from shared.dependencies.repositories import get_post_request_repository
from shared.dependencies.services.get_scheduler import get_scheduler

from abstractions.services.posting import PostingServiceInterface
from services.posting import PostingService
from user_bot.settings import settings


def get_posting_service() -> PostingServiceInterface:
    return PostingService(
        posts_requests_repository=get_post_request_repository(),
        scheduler=get_scheduler(settings.scheduler.job_store_sqlite_path),
    )
