from shared.dependencies.repositories.story_to_publish import get_story_to_publish_repository

from abstractions.services.story_to_publish import StoryToPublishServiceInterface
from services.story_to_publish import StoryToPublishService


def get_story_to_publish_service() -> StoryToPublishServiceInterface:
    return StoryToPublishService(
        story_to_publish_repository=get_story_to_publish_repository()
    )

