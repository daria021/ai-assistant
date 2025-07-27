from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from shared.domain.dto.emoji import CreateEmojiDTO
from shared.domain.models.emoji import Emoji


class EmojiServiceInterface(ABC):
    @abstractmethod
    async def create_emoji(self, emoji: CreateEmojiDTO) -> UUID:
        ...

    @abstractmethod
    async def get_all_emojis(self) -> list[Emoji]:
        ...

    @abstractmethod
    async def get_emoji_by_custom_emoji_id(self, custom_emoji_id: int) -> Optional[Emoji]:
        ...

    @abstractmethod
    async def remove_added_emoji(self, emoji_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_existing_custom_ids(self, ids: list[str]) -> list[str]:
        ...
