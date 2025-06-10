from shared.abstractions.repositories import PostRepositoryInterface
from shared.infrastructure.main_db.repositories import PostRepository
from .sessionmaker import get_session_maker


def get_post_repository() -> PostRepositoryInterface:
    return PostRepository(
        session_maker=get_session_maker(),
    )
