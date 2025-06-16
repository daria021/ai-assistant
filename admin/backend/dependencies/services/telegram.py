from abstractions.services.telegram import TelegramServiceInterface
from services.telegram import TelegramService
from settings import settings


def get_telegram_service() -> TelegramServiceInterface:
    return TelegramService(
        api_id=settings.service_account.api_id,
        api_hash=settings.service_account.api_hash,
        service_session_string=settings.service_account.session_string.get_secret_value(),
        proxy=settings.service_account.proxy,
        service_bot_token=settings.service_account.service_bot_token.get_secret_value(),
        use_bot_for_service=settings.service_account.use_bot_for_service,
    )
