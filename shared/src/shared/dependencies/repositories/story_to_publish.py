from shared.abstractions.repositories import StoryToPublishRepositoryInterface
from shared.infrastructure.main_db.repositories import StoryToPublishRepository
from .sessionmaker import get_session_maker


def get_story_to_publish_repository() -> StoryToPublishRepositoryInterface:
    return StoryToPublishRepository(
        session_maker=get_session_maker(),
    )
