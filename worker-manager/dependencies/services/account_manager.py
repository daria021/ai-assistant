from pathlib import Path

from shared.dependencies.repositories import get_user_repository
from shared.dependencies.repositories.worker_message import get_worker_message_repository

from abstractions.services.manager import AccountManagerInterface
from dependencies.services.bot_service import get_bot_service
from dependencies.services.container_manager import get_container_manager
from dependencies.services.watcher_client import get_watcher_client
from services.account_manager import AccountManager
from settings import settings


def get_account_manager() -> AccountManagerInterface:
    return AccountManager(
        container_manager=get_container_manager(),
        worker_message_repository=get_worker_message_repository(),
        user_repository=get_user_repository(),
        watcher_client=get_watcher_client(),

        app_root_config_path=Path(settings.docker.app_root_config_path),
        api_id=settings.worker.api_id,
        api_hash=settings.worker.api_hash,
        bot_service=get_bot_service()
    )
