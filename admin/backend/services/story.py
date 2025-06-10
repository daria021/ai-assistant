from dataclasses import dataclass
from typing import List
from uuid import UUID

from shared.abstractions.repositories.story import StoryRepositoryInterface
from shared.domain.dto.story import CreateStoryDTO, UpdateStoryDTO
from shared.domain.models.story import Story

from abstractions.services.story import StoryServiceInterface


@dataclass
class StoryService(StoryServiceInterface):
    story_repository: StoryRepositoryInterface

    async def get_all_stories(self) -> List[Story]:
        return await self.story_repository.get_all()

    async def create_story(self, story: CreateStoryDTO) -> UUID:
        return await self.story_repository.create(story)

    async def get_story(self, story_id: UUID) -> Story:   # todo: image path
        return await self.story_repository.get(story_id)

    async def update_story(self, story_id: UUID, story: UpdateStoryDTO) -> None:
        return await self.story_repository.update(story_id, story)

    async def delete_story(self, story_id: UUID) -> None:
        return await self.story_repository.delete(story_id)
