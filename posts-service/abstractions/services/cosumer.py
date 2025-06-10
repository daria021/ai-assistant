from abc import ABC

from shared.abstractions.services import ConsumerInterface

from abstractions.services.posting import PostingServiceInterface


class PostsConsumerInterface(
    ConsumerInterface[PostingServiceInterface],
    ABC,
):
    ...
