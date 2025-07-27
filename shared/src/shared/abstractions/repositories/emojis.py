from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from ...domain.dto.emoji import CreateEmojiDTO, UpdateEmojiDTO
from ...domain.models.emoji import Emoji


class EmojisRepositoryInterface(
    UUIDPKRepositoryInterface[Emoji, CreateEmojiDTO, UpdateEmojiDTO],
    ABC,
):
    @abstractmethod
    async def get_by_custom_emoji_id(self, custom_emoji_id: int) -> Optional[Emoji]:
        ...

    @abstractmethod
    async def get_existing_custom_ids(self, ids: list[str]) -> set[str]:
        ...

    @abstractmethod
    async def remove(self, emoji_id: UUID) -> None:
        ...
