from shared.dependencies.repositories.update_post import get_update_post_repository

from abstractions.services.update_post import UpdatePostServiceInterface
from services.update_post import UpdatePostService


def get_update_post_service() -> UpdatePostServiceInterface:
    return UpdatePostService(
        update_post_repository=get_update_post_repository()
    )
