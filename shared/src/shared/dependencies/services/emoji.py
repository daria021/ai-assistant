from shared.abstractions.services.emoji import EmojiServiceInterface
from shared.dependencies.repositories.emoji import get_emoji_repository
from shared.services.emoji import EmojiService


def get_emoji_service() -> EmojiServiceInterface:
    return EmojiService(emoji_repository=get_emoji_repository())