from shared.dependencies.repositories import get_post_request_repository
from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository
from shared.dependencies.repositories.worker_message import get_worker_message_repository

from abstractions.services.messages import MessageServiceInterface
from dependencies.services.requests import get_requests_service
from services.messages import MessageService


def get_messages_service() -> MessageServiceInterface:
    return MessageService(
        worker_message_repository=get_worker_message_repository(),
        post_requests_repository=get_post_request_repository(),
        posts_to_publish_repository=get_post_to_publish_repository(),
        requests_service=get_requests_service(),
    )