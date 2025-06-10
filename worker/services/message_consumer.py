import logging
from asyncio import sleep
from dataclasses import dataclass
from datetime import datetime
from typing import NoReturn

from shared.abstractions.repositories.worker_message import WorkerMessageRepositoryInterface
from shared.abstractions.services.watcher_client import WatcherClientInterface
from shared.domain.dto import UpdateWorkerMessageDTO
from shared.domain.enums import WorkerMessageStatus
from shared.domain.requests import MessageSentRequest, PostMessageSentRequest

from abstractions.services.message_consumer import MessageConsumerInterface
from abstractions.services.sender import SenderInterface
from services.exceptions import NoMessagesShutdown, CannotSendMessageException

logger = logging.getLogger(__name__)

@dataclass
class MessageConsumer(MessageConsumerInterface):
    sender: SenderInterface
    worker_messages_repository: WorkerMessageRepositoryInterface
    watcher_client: WatcherClientInterface

    global_delay: int = 1
    shutdown_delay: int = 60

    async def execute(self) -> NoReturn:
        to_shutdown = False
        while True:
            message = await self.worker_messages_repository.get_queued_message()
            logger.info(f"message: {message}")
            if not message:
                if to_shutdown:
                    raise NoMessagesShutdown

                to_shutdown = True
                await sleep(self.shutdown_delay)
                continue

            await self.worker_messages_repository.set_message_status(
                message_id=message.id,
                status=WorkerMessageStatus.IN_PROGRESS,
            )

            try:
                await self.sender.send(message)
                await self.worker_messages_repository.set_message_status(
                    message_id=message.id,
                    status=WorkerMessageStatus.SENT,
                    sent_at=datetime.now(),
                )
                report = PostMessageSentRequest(
                    message_id=message.id,
                )
                await self.watcher_client.report_message_sent(report)
            except CannotSendMessageException:
                await self.worker_messages_repository.set_message_status(
                    message_id=message.id,
                    status=WorkerMessageStatus.FAILED,
                )
                logger.error("Cannot send message", exc_info=True)
            except Exception as e:
                logger.error(e, exc_info=True)
                await self.worker_messages_repository.set_message_status(
                    message_id=message.id,
                    status=WorkerMessageStatus.FAILED,
                )


            await sleep(self.global_delay)
