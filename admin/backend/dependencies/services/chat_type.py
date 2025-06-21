from shared.dependencies.repositories.chat_type import get_chat_type_repository

from abstractions.services.chat_type import ChatTypeServiceInterface
from services.chat_type import ChatTypeService


def get_chat_type_service() -> ChatTypeServiceInterface:
    return ChatTypeService(
        chats_type_repository=get_chat_type_repository()
    )
