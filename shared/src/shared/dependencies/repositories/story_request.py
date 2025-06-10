from shared.abstractions.repositories import PublishStoryRequestRepositoryInterface
from shared.infrastructure.main_db.repositories import PublishStoryRequestRepository
from .sessionmaker import get_session_maker


def get_story_request_repository() -> PublishStoryRequestRepositoryInterface:
    return PublishStoryRequestRepository(
        session_maker=get_session_maker(),
    )
