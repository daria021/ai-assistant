from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository

from abstractions.services.cosumer import PostsConsumerInterface
from dependencies.services.posting import get_posting_service
from services.consumer import PostsConsumer


def get_posts_consumer() -> PostsConsumerInterface:
    return PostsConsumer(
        posting_service=get_posting_service(),
        posts_to_publish_repository=get_post_to_publish_repository(),
    )
