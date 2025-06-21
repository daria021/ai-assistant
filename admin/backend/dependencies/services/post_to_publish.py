from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository

from abstractions.services.post_to_publish import PostToPublishServiceInterface
from dependencies.services.upload import get_upload_service
from dependencies.services.user import get_user_service
from services.post_to_publish import PostToPublishService


def get_post_to_publish_service() -> PostToPublishServiceInterface:
    return PostToPublishService(
        post_to_publish_repository=get_post_to_publish_repository(),
        upload_service=get_upload_service(),
        user_service=get_user_service()
    )

