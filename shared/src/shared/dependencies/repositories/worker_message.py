from shared.abstractions.repositories.worker_message import WorkerMessageRepositoryInterface
from shared.infrastructure.main_db.repositories.worker_message import WorkerMessageRepository
from .sessionmaker import get_session_maker


def get_worker_message_repository() -> WorkerMessageRepositoryInterface:
    return WorkerMessageRepository(
        session_maker=get_session_maker(),
    )
