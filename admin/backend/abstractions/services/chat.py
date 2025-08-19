from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.domain.dto import UpdateChatDTO
from shared.domain.models import Chat


class ChatServiceInterface(ABC):

    @abstractmethod
    async def get_chats(self) -> list[Chat]:
        ...

    @abstractmethod
    async def update_chat(self, chat_id: UUID, chat: UpdateChatDTO) -> Chat:
        ...

    @abstractmethod
    async def delete_chat(self, chat_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_chats_by_type(self, type_id: UUID) -> list[Chat]:
        ...

    @abstractmethod
    async def create_chat_by_link(
            self,
            invite_link: str,
            manager_id: UUID,
            type_id: Optional[UUID] = None,
    ) -> Chat:
        ...
