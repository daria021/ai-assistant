from shared.abstractions.repositories.chat_type import ChatTypeRepositoryInterface
from shared.infrastructure.main_db.repositories.chat_type import ChatTypeRepository
from .sessionmaker import get_session_maker


def get_chat_type_repository() -> ChatTypeRepositoryInterface:
    return ChatTypeRepository(
        session_maker=get_session_maker(),
    )
