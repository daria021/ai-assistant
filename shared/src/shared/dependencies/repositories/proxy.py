from shared.abstractions.repositories import ProxyRepositoryInterface
from shared.infrastructure.main_db.repositories import ProxyRepository
from .sessionmaker import get_session_maker


def get_proxy_repository() -> ProxyRepositoryInterface:
    return ProxyRepository(
        session_maker=get_session_maker(),
    )
