from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from shared.domain.dto.post_to_publish import CreatePostToPublishDTO, UpdatePostToPublishDTO
from shared.domain.models.post_to_publish import PostToPublish


class PostToPublishServiceInterface(ABC):

    @abstractmethod
    async def get_posts_to_publish(self, user_id: UUID) -> List[PostToPublish]:
        ...

    @abstractmethod
    async def create_post_to_publish(self, post_to_publish: CreatePostToPublishDTO) -> UUID:
        ...

    @abstractmethod
    async def get_post_to_publish(self, post_to_publish_id: UUID) -> PostToPublish:
        ...

    @abstractmethod
    async def update_post_to_publish(self, post_to_publish_id: UUID, post_to_publish: UpdatePostToPublishDTO) -> None:
        ...

    @abstractmethod
    async def delete_post_to_publish(self, post_to_publish_id: UUID) -> None:
        ...