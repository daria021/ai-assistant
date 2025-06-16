import logging
from asyncio import sleep
from dataclasses import dataclass
from typing import NoReturn

from abstractions.services.manager import AccountManagerInterface
from abstractions.services.sending_consumer import SendingConsumerInterface
from abstractions.services.sending_request import SendingRequestServiceInterface

logger = logging.getLogger(__name__)


@dataclass
class SendingConsumer(SendingConsumerInterface):
    account_manager: AccountManagerInterface
    sending_request_service: SendingRequestServiceInterface

    idle_delay: float = 5
    global_delay: float = 5

    async def execute(self) -> NoReturn:
        while True:
            message_to_send = await self.sending_request_service.get_queued_message()
            if message_to_send is None:
                await sleep(self.idle_delay)
                continue

            logger.info(f"new message! {message_to_send.id}")
            await self.sending_request_service.set_in_progress(message_to_send)

            try:
                await self.account_manager.send(message_to_send)
            except Exception as e:
                logger.error(e, exc_info=True)
                await self.sending_request_service.set_failed(message_to_send)

            await sleep(self.global_delay)
