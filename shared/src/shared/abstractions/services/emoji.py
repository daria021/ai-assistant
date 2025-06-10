from abc import ABC, abstractmethod
from uuid import UUID

from shared.domain.dto.emoji import CreateEmojiDTO
from shared.domain.models.emoji import Emoji


class EmojiServiceInterface(ABC):

    @abstractmethod
    async def create_emoji(self, emoji: CreateEmojiDTO) -> UUID:
        ...

    @abstractmethod
    async def get_all_emojis(self) -> list[Emoji]:
        ...

