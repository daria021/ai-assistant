from shared.dependencies.repositories import get_chat_repository

from abstractions.services.chat import ChatServiceInterface
from dependencies.services.telegram import get_telegram_service
from services.chat import ChatService


def get_chat_service() -> ChatServiceInterface:
    return ChatService(
        chats_repository=get_chat_repository(),
        telegram_service=get_telegram_service(),
    )
