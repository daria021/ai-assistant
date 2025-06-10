from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.dependencies.services.watcher_client import get_watcher_client_from_url

from settings import settings


def get_watcher_client() -> WatcherClientInterface:
    return get_watcher_client_from_url(
        base_url=settings.watcher.url,
    )
