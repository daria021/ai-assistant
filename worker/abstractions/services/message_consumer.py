from abc import ABC

from shared.abstractions.services.consumer import ConsumerInterface

from abstractions.services.sender import SenderInterface


class MessageConsumerInterface(
    ConsumerInterface[SenderInterface],
    ABC,
):
    ...
