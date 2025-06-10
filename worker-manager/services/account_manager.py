import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.domain.models import SendingRequest
from shared.abstractions.repositories import UserRepositoryInterface
from shared.abstractions.repositories.worker_message import WorkerMessageRepositoryInterface
from shared.domain.dto import CreateWorkerMessageDTO
from shared.domain.models import SendPostRequest, UserWithSessionString
from shared.domain.enums import WorkerMessageType, WorkerMessageStatus
from shared.settings.worker import WorkerSettings

from abstractions.services.container_manager import ContainerManagerInterface
from abstractions.services.manager import AccountManagerInterface
from services.exceptions import UnknownRequestTypeException

logger = logging.getLogger(__name__)

@dataclass
class AccountManager(AccountManagerInterface):
    container_manager: ContainerManagerInterface
    worker_message_repository: WorkerMessageRepositoryInterface
    user_repository: UserRepositoryInterface

    watcher_client: WatcherClientInterface

    app_root_config_path: Path
    api_id: int
    api_hash: str

    async def send(self, request: SendingRequest) -> None:
        if isinstance(request, SendPostRequest):
            await self._send_post(request)
            return

        raise UnknownRequestTypeException(f"{type(request)} requests are not supported")

    async def _send_post(self, request: SendPostRequest) -> None:
        worker_message_dto = CreateWorkerMessageDTO(
            user_id=request.user_id,
            type=WorkerMessageType.POST,
            text=request.post.text,
            entities=request.post.entities,
            media_path=request.post.image_path,
            status=WorkerMessageStatus.PENDING,
            chat_id=request.chat.chat_id,
            request_id=request.id,
        )

        logger.info(f"Sending post request {worker_message_dto}")
        logger.info(f"Request was {request}")

        await self.worker_message_repository.create(worker_message_dto)

        await self.ensure_worker_running(request.user_id)

    async def ensure_worker_running(self, user_id: UUID) -> None:
        user = await self.user_repository.get(user_id)

        if await self.container_manager.check_for_active_worker(user.id):
            return

        worker_settings = self._make_worker_settings(user)
        worker_settings_file = self.settings_to_file(worker_settings)

        logger.info(worker_settings.model_dump())
        logger.info(worker_settings_file)
        with worker_settings_file.open('rt') as f:
            logger.info(f.read())

        await self.container_manager.start_container(
            worker_id=worker_settings.user.id,
            config_path=worker_settings_file,
        )

    def _make_worker_settings(self, user: UserWithSessionString) -> WorkerSettings:
        return WorkerSettings(
            user=user,
            api_id=self.api_id,
            api_hash=self.api_hash,
        )

    def settings_to_file(self, settings: WorkerSettings) -> Path:
        filename = f"{settings.user.telegram_username}.{uuid4()}.json"
        file_path = self.app_root_config_path / filename

        if isinstance(settings, WorkerSettings):
            structured_settings = settings.model_dump_json(
                indent=4,
            )
            with file_path.open('wt') as f:
                f.write(structured_settings)
        else:
            raise Exception('Settings should be of type WorkerSettings')

        return file_path
