from abstractions.services.watcher import WatcherInterface
from dependencies.services.messages import get_messages_service
from dependencies.services.publication import get_publication_service
from dependencies.services.requests import get_requests_service
from services.watcher import Watcher


def get_watcher() -> WatcherInterface:
    return Watcher(
        publication_service=get_publication_service(),
        requests_service=get_requests_service(),
        message_service=get_messages_service(),
    )
