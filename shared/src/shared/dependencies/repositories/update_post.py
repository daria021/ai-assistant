from shared.abstractions.repositories.update_post import UpdatePostRepositoryInterface
from shared.dependencies.repositories.sessionmaker import get_session_maker
from shared.infrastructure.main_db.repositories.update_post import UpdatePostRepository


def get_update_post_repository() -> UpdatePostRepositoryInterface:
    return UpdatePostRepository(
        session_maker=get_session_maker()
    )