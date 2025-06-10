from dataclasses import dataclass
from typing import List
from uuid import UUID

from shared.abstractions.repositories.story_to_publish import StoryToPublishRepositoryInterface
from shared.domain.dto.story_to_publish import CreateStoryToPublishDTO, UpdateStoryToPublishDTO
from shared.domain.models.story import Story
from shared.infrastructure.main_db.repositories.story_to_publish import StoryToPublishRepository

from abstractions.services.story_to_publish import StoryToPublishServiceInterface

from shared.domain.models import StoryToPublish


@dataclass
class StoryToPublishService(StoryToPublishServiceInterface):
    story_to_publish_repository: StoryToPublishRepositoryInterface

    async def get_all_stories_to_publish(self) -> List[Story]:
        return await self.story_to_publish_repository.get_all()

    async def create_story_to_publish(self, story_to_publish: CreateStoryToPublishDTO) -> UUID:
        return await self.story_to_publish_repository.create(story_to_publish)

    async def get_story_to_publish(self, story_to_publish_id: UUID) -> StoryToPublish:   # todo: image path
        return await self.story_to_publish_repository.get(story_to_publish_id)

    async def update_story_to_publish(self, story_to_publish_id: UUID,
                                      story_to_publish: UpdateStoryToPublishDTO) -> None:
        return await self.story_to_publish_repository.update(story_to_publish_id, story_to_publish)

    async def delete_story_to_publish(self, story_to_publish_id: UUID) -> None:
        return await self.story_to_publish_repository.delete(story_to_publish_id)