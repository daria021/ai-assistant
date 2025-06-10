from shared.dependencies.repositories import get_post_request_repository

from abstractions.services.sending_request import SendingRequestServiceInterface
from services.sending_request import SendingRequestService


def get_sending_request_service() -> SendingRequestServiceInterface:
    return SendingRequestService(
        post_request_repository=get_post_request_repository(),
    )
