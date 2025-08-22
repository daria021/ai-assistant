from dataclasses import dataclass
from typing import List
from uuid import UUID

from shared.abstractions.repositories import PostRepositoryInterface
from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.models import Post

from abstractions.services.post import PostServiceInterface
from shared.abstractions.services import UploadServiceInterface


@dataclass
class PostService(PostServiceInterface):
    post_repository: PostRepositoryInterface
    upload_service: UploadServiceInterface

    async def get_all_posts(self) -> List[Post]:
        return await self.post_repository.get_all()

    async def create_post(self, post: CreatePostDTO) -> UUID:
        return await self.post_repository.create(post)

    async def get_post(self, post_id: UUID) -> Post:
        post = await self.post_repository.get(post_id)

        file_path = self.upload_service.get_file_url(post.image_path)

        post.image_path = file_path
        return post

    async def update_post(self, post_id: UUID, post: UpdatePostDTO) -> Post:
        return await self.post_repository.update(post_id, post)

    async def delete_post(self, post_id: UUID) -> None:
        return await self.post_repository.delete(post_id)
