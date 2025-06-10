from shared.abstractions.repositories import UserRepositoryInterface
from shared.infrastructure.main_db.repositories import UserRepository
from .sessionmaker import get_session_maker


def get_user_repository() -> UserRepositoryInterface:
    return UserRepository(
        session_maker=get_session_maker(),
    )
