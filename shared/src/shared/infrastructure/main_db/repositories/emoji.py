from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete

from shared.abstractions.repositories.emojis import EmojisRepositoryInterface
from shared.domain.dto.emoji import CreateEmojiDTO, UpdateEmojiDTO
from shared.domain.models.emoji import Emoji as EmojiModel
from shared.infrastructure.main_db.entities import Emoji
from .abstract import AbstractMainDBRepository


@dataclass
class EmojiRepository(
    AbstractMainDBRepository[Emoji, EmojiModel, CreateEmojiDTO, UpdateEmojiDTO],
    EmojisRepositoryInterface,
):
    async def get_by_custom_emoji_id(self, custom_emoji_id: int) -> Optional[EmojiModel]:
        async with self.session_maker() as session:
            res = await session.execute(
                select(self.entity)
                .where(self.entity.custom_emoji_id == custom_emoji_id)
            )
            obj = res.scalars().one_or_none()

        return self.entity_to_model(obj) if obj else None

    async def get_existing_custom_ids(self, ids: list[str]) -> set[str]:
        if not ids:
            return set()

        async with self.session_maker() as session:
            res = await session.execute(
                select(self.entity.custom_emoji_id)
                .where(self.entity.custom_emoji_id.in_(ids))
            )
            return set(res.scalars().all())

    async def remove(self, emoji_id: UUID) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                emoji = await session.get(self.entity, emoji_id)
                await session.delete(emoji)

    def create_dto_to_entity(self, dto: CreateEmojiDTO) -> Emoji:
        return Emoji(
            id=dto.id,
            name=dto.name,
            custom_emoji_id=dto.custom_emoji_id,
            img_url=dto.img_url,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Emoji) -> Emoji:
        return EmojiModel(
            id=entity.id,
            name=entity.name,
            custom_emoji_id=entity.custom_emoji_id,
            img_url=entity.img_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
