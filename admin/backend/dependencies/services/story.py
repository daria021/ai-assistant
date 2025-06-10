from shared.dependencies.repositories import get_story_repository

from abstractions.services.story import StoryServiceInterface
from services.story import StoryService


def get_story_service() -> StoryServiceInterface:
    return StoryService(
        story_repository=get_story_repository()
    )

