from shared.dependencies.repositories import get_user_repository, get_proxy_repository

from abstractions.services.user import UserServiceInterface
from dependencies.services.telegram import get_telegram_service
from services.user import UserService


def get_user_service() -> UserServiceInterface:
    return UserService(
        user_repository=get_user_repository(),
        telegram_service=get_telegram_service(),
        proxy_repository=get_proxy_repository(),
    )