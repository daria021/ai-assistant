from shared.abstractions.repositories.emojis import EmojisRepositoryInterface
from shared.infrastructure.main_db.repositories.emoji import EmojiRepository
from .sessionmaker import get_session_maker


def get_emoji_repository() -> EmojisRepositoryInterface:
    return EmojiRepository(
        session_maker=get_session_maker(),
    )
