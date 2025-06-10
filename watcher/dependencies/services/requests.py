from shared.dependencies.repositories import get_post_request_repository
from shared.dependencies.repositories.worker_message import get_worker_message_repository

from abstractions.services.requests import SendingRequestsServiceInterface
from dependencies.services.publication import get_publication_service
from services.requests import SendingRequestsService


def get_requests_service() -> SendingRequestsServiceInterface:
    return SendingRequestsService(
        post_requests_repository=get_post_request_repository(),
        messages_repository=get_worker_message_repository(),
        publication_service=get_publication_service(),
    )
