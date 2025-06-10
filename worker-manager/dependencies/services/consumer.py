from abstractions.services.sending_consumer import SendingConsumerInterface
from dependencies.services.account_manager import get_account_manager
from dependencies.services.sending_request import get_sending_request_service
from services.sending_consumer import SendingConsumer


def get_consumer() -> SendingConsumerInterface:
    return SendingConsumer(
        account_manager=get_account_manager(),
        sending_request_service=get_sending_request_service(),
    )
