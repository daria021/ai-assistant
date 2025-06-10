from shared.dependencies.repositories import get_post_request_repository
from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository

from abstractions.services.publication import PublicationServiceInterface
from services.publication import PublicationService


def get_publication_service() -> PublicationServiceInterface:
    return PublicationService(
        post_to_publish_repository=get_post_to_publish_repository(),
        posts_request_repository=get_post_request_repository(),
    )
