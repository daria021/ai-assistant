from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import select

from shared.abstractions.repositories import PublishStoryRequestRepositoryInterface
from shared.domain.dto import CreatePublishStoryRequestDTO, UpdatePublishStoryRequestDTO
from shared.domain.enums import PublishStoryRequestStatus
from shared.domain.models import (
    Story as StoryModel,
    PublishStoryRequest as PublishStoryRequestModel,
    User as UserModel,
)
from shared.infrastructure.main_db.entities import Story, PublishStoryRequest, User
from .abstract import AbstractMainDBRepository


@dataclass
class PublishStoryRequestRepository(
    AbstractMainDBRepository[
        PublishStoryRequest, PublishStoryRequestModel, CreatePublishStoryRequestDTO, UpdatePublishStoryRequestDTO],
    PublishStoryRequestRepositoryInterface,
):
    joined_fields: dict[str, Optional[list[str]]] = field(default_factory=lambda: {
        "user": None,
        "story": None,
    })

    async def get_queued_message(self) -> Optional[PublishStoryRequest]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(self.entity)
                .where(self.entity.status == PublishStoryRequestStatus.PLANNED)
                .order_by(self.entity.created_at)
                .options(*self.options)
                .limit(1)
            )  # todo: batching?

            message = result.unique().scalars().one_or_none()

        return self.entity_to_model(message) if message else None

    def create_dto_to_entity(self, dto: CreatePublishStoryRequestDTO) -> PublishStoryRequest:
        return PublishStoryRequest(
            id=dto.id,
            story_id=dto.story_id,
            user_id=dto.user_id,
            scheduled_at=dto.scheduled_at,
            status=dto.status,
            published_at=dto.published_at,
            publication_id=dto.publication_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: PublishStoryRequest) -> PublishStoryRequest:
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
                name=story.name,
                text=story.text,
                file_path=story.file_path,
                created_at=story.created_at,
                updated_at=story.updated_at,
            )

        return PublishStoryRequestModel(
            id=entity.id,
            story_id=entity.story_id,
            user_id=entity.user_id,
            scheduled_at=entity.scheduled_at,
            status=entity.status,
            published_at=entity.published_at,
            publication_id=entity.publication_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            user=_map_user(entity.user),
            story=_map_story(entity.story),
        )
