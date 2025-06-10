from dataclasses import dataclass

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
