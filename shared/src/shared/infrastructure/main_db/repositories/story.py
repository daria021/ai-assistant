from dataclasses import dataclass

from shared.abstractions.repositories.story import StoryRepositoryInterface
from shared.domain.dto.story import CreateStoryDTO, UpdateStoryDTO
from shared.domain.models.story import Story as StoryModel
from shared.infrastructure.main_db.entities import Story
from shared.infrastructure.main_db.repositories.abstract import AbstractMainDBRepository


@dataclass
class StoryRepository(
    AbstractMainDBRepository[Story, StoryModel, CreateStoryDTO, UpdateStoryDTO],
    StoryRepositoryInterface,
):
    def create_dto_to_entity(self, dto: CreateStoryDTO) -> Story:
        return Story(
            id=dto.id,
            name=dto.name,
            text=dto.text,
            file_path=dto.file_path,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Story) -> StoryModel:
        return StoryModel(
            id=entity.id,
            name=entity.name,
            text=entity.text,
            file_path=entity.file_path,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )