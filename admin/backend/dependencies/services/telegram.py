from abstractions.services.telegram import TelegramServiceInterface
from services.telegram import TelegramService
from settings import settings


def get_telegram_service() -> TelegramServiceInterface:
    return TelegramService(
        api_id=settings.service_account.api_id,
        api_hash=settings.service_account.api_hash,
        service_session_string=settings.service_account.session_string.get_secret_value(),
    )
