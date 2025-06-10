from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.services.watcher_client import WatcherClient


def get_watcher_client_from_url(base_url: str) -> WatcherClientInterface:
    return WatcherClient(
        base_url=base_url,
    )
