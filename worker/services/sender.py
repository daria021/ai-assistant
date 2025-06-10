from dataclasses import dataclass

from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.domain.enums import WorkerMessageType
from shared.domain.models import WorkerMessage
from shared.domain.requests import PostMessageSentRequest

from abstractions.repositories import TelegramMessagesRepositoryInterface
from abstractions.services.sender import SenderInterface
from services.exceptions import CannotSendMessageException


@dataclass
class Sender(SenderInterface):
    messenger: TelegramMessagesRepositoryInterface

    async def send(self, message: WorkerMessage):
        match message.type:
            case WorkerMessageType.POST:
                await self._send_post(message)

    async def _send_post(self, message: WorkerMessage):
        try:
            await self.messenger.send_message(
                chat_id=message.chat_id,
                text=message.text,
                entities=message.entities,
                media_path=message.media_path,
            )
        except Exception as e:
            raise CannotSendMessageException from e
