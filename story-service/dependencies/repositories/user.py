from backend.abstractions.repositories import UserRepositoryInterface
from backend.dependencies.repositories.session_maker import get_session_maker
from infrastructure.repositories.user import UserRepository


def get_user_repository() -> UserRepositoryInterface:
    return UserRepository(
        session_maker=get_session_maker()
    )