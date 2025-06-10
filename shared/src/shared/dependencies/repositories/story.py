from shared.abstractions.repositories import StoryRepositoryInterface
from shared.infrastructure.main_db import StoryRepository
from .sessionmaker import get_session_maker


def get_story_repository() -> StoryRepositoryInterface:
    return StoryRepository(
        session_maker=get_session_maker(),
    )
