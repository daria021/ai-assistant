from datetime import timedelta

from shared.dependencies.repositories import get_post_request_repository

from abstractions.services.sending_request import SendingRequestServiceInterface
from services.sending_request import SendingRequestService
from settings import settings
from dependencies.services.watcher_client import get_watcher_client


def get_sending_request_service() -> SendingRequestServiceInterface:
    return SendingRequestService(
        post_request_repository=get_post_request_repository(),
        stale_threshold=timedelta(minutes=settings.worker.stale_threshold_minutes),
        watcher_client=get_watcher_client(),
    )
