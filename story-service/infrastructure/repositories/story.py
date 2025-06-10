import logging
from dataclasses import dataclass

from sqlalchemy import select

from abstractions.repositories.story import StoryRepositoryInterface
from domain.dto.story import CreateStoryDTO, UpdateStoryDTO
from domain.models.story import Story as StoryModel
from infrastructure.entities import Story
from infrastructure.repositories.sqlalchemy import AbstractSQLAlchemyRepository

logger = logging.getLogger(__name__)


@dataclass
class StoryRepository(
    AbstractSQLAlchemyRepository[Story, StoryModel, CreateStoryDTO, UpdateStoryDTO],
    StoryRepositoryInterface,
):

    async def get_by_telegram_id(self, telegram_id: int) -> Story:
        async with self.session_maker() as session:
            Story = await session.execute(
                select(self.entity)
                .where(self.entity.telegram_id == telegram_id)
                .options(*self.options)
            )
            Story = Story.unique().scalars().one_or_none()

        return self.entity_to_model(Story) if Story else None


    def create_dto_to_entity(self, dto: CreateStoryDTO) -> Story:
        return Story(
            id=dto.id,
            manager_id=dto.manager_id,
            file_path=dto.file_path,
            scheduled_time=dto.scheduled_time,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Story) -> StoryModel:
        return StoryModel(
            id=entity.id,
            manager_id=entity.manager_id,
            file_path=entity.file_path,
            scheduled_time=entity.scheduled_time,
            status=entity.status,
            manager=entity.manager,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
