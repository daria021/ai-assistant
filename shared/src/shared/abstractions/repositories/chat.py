from abc import ABC, abstractmethod

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto.chat import CreateChatDTO, UpdateChatDTO
from shared.domain.models.chat import Chat


class ChatRepositoryInterface(
    UUIDPKRepositoryInterface[Chat, CreateChatDTO, UpdateChatDTO],
    ABC,
):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Chat:
        ...

    @abstractmethod
    async def get_by_invite_link(self, invite_link: str) -> Chat:
        ...
