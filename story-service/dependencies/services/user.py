from backend.abstractions.services.user import UserServiceInterface
from backend.dependencies.repositories.user import get_user_repository
from backend.services.user import UserService


def get_user_service() -> UserServiceInterface:
    return UserService(
        user_repository=get_user_repository()
    )