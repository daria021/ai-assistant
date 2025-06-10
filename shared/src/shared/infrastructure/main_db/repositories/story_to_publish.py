from dataclasses import dataclass, field
from typing import Optional

from shared.abstractions.repositories import StoryToPublishRepositoryInterface
from shared.domain.dto import CreateStoryToPublishDTO, UpdateStoryToPublishDTO
from shared.domain.models import StoryToPublish as StoryToPublishModel, User as UserModel, Story as StoryModel
from shared.infrastructure.main_db.entities import StoryToPublish, User, Story
from .abstract import AbstractMainDBRepository


@dataclass
class StoryToPublishRepository(
    AbstractMainDBRepository[StoryToPublish, StoryToPublishModel, CreateStoryToPublishDTO, UpdateStoryToPublishDTO],
    StoryToPublishRepositoryInterface,
):
    joined_fields: dict[str, Optional[list[str]]] = field(default_factory=lambda: {
        "manager": None,
        "story": None,
    })

    def create_dto_to_entity(self, dto: CreateStoryToPublishDTO) -> StoryToPublish:
        return StoryToPublish(
            id=dto.id,
            story_id=dto.story_id,
            manager_id=dto.manager_id,
            scheduled_type=dto.scheduled_type,
            scheduled_date=dto.scheduled_date,
            scheduled_time=dto.scheduled_time,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: StoryToPublish) -> StoryToPublishModel:
        def _map_user(user: User) -> UserModel:
            return UserModel(
                id=user.id,
                telegram_id=user.telegram_id,
                telegram_username=user.telegram_username,
                telegram_last_name=user.telegram_last_name,
                telegram_first_name=user.telegram_first_name,
                telegram_language_code=user.telegram_language_code,
                role=user.role,
                assistant_enabled=user.assistant_enabled,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

        def _map_story(story: Story) -> StoryModel:
            return StoryModel(
                id=story.id,
                text=story.text,
                name=story.name,
                file_path=story.file_path,
                created_at=story.created_at,
                updated_at=story.updated_at,
            )

        return StoryToPublishModel(
            id=entity.id,
            story_id=entity.story_id,
            manager_id=entity.manager_id,
            scheduled_type=entity.scheduled_type,
            scheduled_date=entity.scheduled_date,
            scheduled_time=entity.scheduled_time,
            status=entity.status,
            manager=_map_user(entity.manager),
            story=_map_story(entity.story),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
