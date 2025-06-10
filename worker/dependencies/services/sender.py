from abstractions.services.sender import SenderInterface
from dependencies.repositories.telegram import get_telegram_message_repository
from services.sender import Sender


def get_sender() -> SenderInterface:
    return Sender(
        messenger=get_telegram_message_repository(),
    )
