from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from shared.domain.dto.story import CreateStoryDTO, UpdateStoryDTO
from shared.domain.models.story import Story


class StoryServiceInterface(ABC):

    @abstractmethod
    async def get_all_stories(self) -> List[Story]:
        ...

    @abstractmethod
    async def create_story(self, story: CreateStoryDTO) -> UUID:
        ...

    @abstractmethod
    async def get_story(self, story_id: UUID) -> Story:
        ...

    @abstractmethod
    async def update_story(self, story_id: UUID, story: UpdateStoryDTO) -> None:
        ...

    @abstractmethod
    async def delete_story(self, story_id: UUID) -> None:
        ...

