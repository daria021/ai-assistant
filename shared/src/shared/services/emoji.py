from dataclasses import dataclass
from typing import List
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

