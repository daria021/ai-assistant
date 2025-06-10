from shared.dependencies.repositories.worker_message import get_worker_message_repository

from abstractions.services.message_consumer import MessageConsumerInterface
from dependencies.services.sender import get_sender
from dependencies.services.watcher_client import get_watcher_client
from services.message_consumer import MessageConsumer


def get_message_consumer() -> MessageConsumerInterface:
    return MessageConsumer(
        sender=get_sender(),
        worker_messages_repository=get_worker_message_repository(),
        watcher_client=get_watcher_client(),
    )
