from shared.dependencies.repositories import get_post_repository

from abstractions.services.post import PostServiceInterface
from dependencies.services.update_post import get_update_post_service
from dependencies.services.upload import get_upload_service
from services.post import PostService


def get_post_service() -> PostServiceInterface:
    return PostService(
        post_repository=get_post_repository(),
        upload_service=get_upload_service(),
        update_post_service=get_update_post_service()
    )

