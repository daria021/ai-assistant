import logging
from dataclasses import dataclass
from uuid import UUID

from shared.abstractions.repositories.chat_type import ChatTypeRepositoryInterface
from shared.domain.dto.chat_type import CreateChatTypeDTO
from shared.domain.models.chat_type import ChatType

from abstractions.services.chat_type import ChatTypeServiceInterface

logger = logging.getLogger(__name__)


@dataclass
class ChatTypeService(ChatTypeServiceInterface):
    chats_type_repository: ChatTypeRepositoryInterface

    async def create_chat_type(self, chat_type: CreateChatTypeDTO) -> UUID:
        return await self.chats_type_repository.create(chat_type)

    async def get_chats_types(self) -> list[ChatType]:
        return await self.chats_type_repository.get_all()

    async def get_chat_type(self, chat_type_id: UUID) -> ChatType:
        return await self.chats_type_repository.get(chat_type_id)

    async def delete_chat_type(self, chat_type_id: UUID) -> None:
        return await self.chats_type_repository.delete(chat_type_id)

