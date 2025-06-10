from shared.abstractions.repositories import PostToPublishRepositoryInterface
from shared.infrastructure.main_db.repositories import PostToPublishRepository
from .sessionmaker import get_session_maker


def get_post_to_publish_repository() -> PostToPublishRepositoryInterface:
    return PostToPublishRepository(
        session_maker=get_session_maker(),
    )
