from abc import ABC

from shared.abstractions.services.consumer import ConsumerInterface

from abstractions.services.manager import AccountManagerInterface


class SendingConsumerInterface(
    ConsumerInterface[AccountManagerInterface],
    ABC,
):
    ...
