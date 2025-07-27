from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from shared.abstractions.repositories.emojis import EmojisRepositoryInterface
from shared.abstractions.services.emoji import EmojiServiceInterface
from shared.domain.dto.emoji import CreateEmojiDTO
from shared.domain.models.emoji import Emoji


@dataclass
class EmojiService(EmojiServiceInterface):
    emoji_repository: EmojisRepositoryInterface

    async def get_all_emojis(self) -> List[Emoji]:
        return await self.emoji_repository.get_all()

    async def create_emoji(self, emoji: CreateEmojiDTO) -> UUID:
        return await self.emoji_repository.create(emoji)

    async def get_emoji_by_custom_emoji_id(self, custom_emoji_id: int) -> Optional[Emoji]:
        return await self.emoji_repository.get_by_custom_emoji_id(custom_emoji_id)

    async def remove_added_emoji(self, emoji_id: UUID) -> None:
        await self.emoji_repository.remove(emoji_id)

    async def get_by_custom_emoji_id(self, emoji_id: UUID) -> None:
        await self.emoji_repository.remove(emoji_id)

    async def get_existing_custom_ids(self, ids: list[int]) -> list[int]:
        return list(await self.emoji_repository.get_existing_custom_ids(ids))
