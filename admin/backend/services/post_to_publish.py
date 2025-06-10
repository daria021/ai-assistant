from dataclasses import dataclass
from typing import List
from uuid import UUID

from shared.abstractions.repositories.post_to_publish import PostToPublishRepositoryInterface
from shared.domain.dto.post_to_publish import CreatePostToPublishDTO, UpdatePostToPublishDTO
from shared.domain.models.post_to_publish import PostToPublish

from abstractions.services.post_to_publish import PostToPublishServiceInterface
from shared.abstractions.services import UploadServiceInterface


@dataclass
class PostToPublishService(PostToPublishServiceInterface):
    post_to_publish_repository: PostToPublishRepositoryInterface
    upload_service: UploadServiceInterface

    async def get_all_posts_to_publish(self) -> List[PostToPublish]:
        return await self.post_to_publish_repository.get_all()

    async def create_post_to_publish(self, post_to_publish: CreatePostToPublishDTO) -> UUID:
        return await self.post_to_publish_repository.create(post_to_publish)

    async def get_post_to_publish(self, post_to_publish_id: UUID) -> PostToPublish:
        post = await self.post_to_publish_repository.get(post_to_publish_id)
        file_path = self.upload_service.get_file_url(post.post.image_path)

        post.post.image_path = file_path
        return post

    async def update_post_to_publish(self, post_to_publish_id: UUID, post_to_publish: UpdatePostToPublishDTO) -> None:
        return await self.post_to_publish_repository.update(post_to_publish_id, post_to_publish)

    async def delete_post_to_publish(self, post_to_publish_id: UUID) -> None:
        return await self.post_to_publish_repository.delete(post_to_publish_id)
