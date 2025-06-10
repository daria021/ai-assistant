from shared.abstractions.repositories import ChatRepositoryInterface
from shared.infrastructure.main_db.repositories import ChatRepository
from .sessionmaker import get_session_maker


def get_chat_repository() -> ChatRepositoryInterface:
    return ChatRepository(
        session_maker=get_session_maker(),
    )
