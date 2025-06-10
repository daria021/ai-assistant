from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from shared.domain.dto.story_to_publish import CreateStoryToPublishDTO, UpdateStoryToPublishDTO
from shared.domain.models.story import Story


class StoryToPublishServiceInterface(ABC):

    @abstractmethod
    async def get_all_stories_to_publish(self) -> List[Story]:
        ...

    @abstractmethod
    async def create_story_to_publish(self, story_to_publish: CreateStoryToPublishDTO) -> UUID:
        ...

    @abstractmethod
    async def get_story_to_publish(self, story_to_publish_id: UUID) -> Story:
        ...

    @abstractmethod
    async def update_story_to_publish(self, story_to_publish_id: UUID, story_to_publish: UpdateStoryToPublishDTO) -> None:
        ...

    @abstractmethod
    async def delete_story_to_publish(self, story_to_publish_id: UUID) -> None:
        ...

