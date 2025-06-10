from abstractions.repositories import TelegramMessagesRepositoryInterface
from infrastructure.repositories.telegram import TelethonTelegramMessagesRepository
from user_bot.settings import settings


def get_telegram_message_repository() -> TelegramMessagesRepositoryInterface:
    return TelethonTelegramMessagesRepository(
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        worker=settings.user,
    )
