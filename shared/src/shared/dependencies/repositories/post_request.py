from shared.abstractions.repositories import SendPostRequestRepositoryInterface
from shared.infrastructure.main_db.repositories import SendPostRequestRepository
from .sessionmaker import get_session_maker


def get_post_request_repository() -> SendPostRequestRepositoryInterface:
    return SendPostRequestRepository(
        session_maker=get_session_maker(),
    )
