from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.dependencies.services.watcher_client import get_watcher_client_from_url

from user_bot.settings import settings


def get_watcher_client() -> WatcherClientInterface:
    return get_watcher_client_from_url(settings.watcher.url)
