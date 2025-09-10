from abc import ABC, abstractmethod
from uuid import UUID

from shared.domain.dto.chat_type import CreateChatTypeDTO, UpdateChatTypeDTO
from shared.domain.models.chat_type import ChatType


class ChatTypeServiceInterface(ABC):

    @abstractmethod
    async def create_chat_type(self, chat_type: CreateChatTypeDTO) -> UUID:
        ...

    @abstractmethod
    async def get_chats_types(self) -> list[ChatType]:
        ...

    @abstractmethod
    async def get_chat_type(self, chat_type_id: UUID) -> ChatType:
        ...

    @abstractmethod
    async def delete_chat_type(self, chat_type_id: UUID) -> None:
        ...

    @abstractmethod
    async def update_chat_type(self, chat_type_id: UUID, chat_type: UpdateChatTypeDTO) -> ChatType:
        ...




