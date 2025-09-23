from dataclasses import dataclass
from typing import List
from uuid import UUID

from shared.abstractions.repositories import PostRepositoryInterface
from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.dto.update_post import CreateUpdatePostDTO, UpdateUpdatePostDTO
from shared.domain.models import Post

from abstractions.services.post import PostServiceInterface
from shared.abstractions.services import UploadServiceInterface

from abstractions.services.update_post import UpdatePostServiceInterface


@dataclass
class PostService(PostServiceInterface):
    post_repository: PostRepositoryInterface
    upload_service: UploadServiceInterface
    update_post_service: UpdatePostServiceInterface

    async def get_all_posts(self) -> List[Post]:
        return await self.post_repository.get_all()

    async def get_templates(self) -> List[Post]:
        return await self.post_repository.get_templates()

    async def create_post(self, post: CreatePostDTO, author_id: UUID) -> UUID:
        update_post = CreateUpdatePostDTO(
            post_id = post.id,
            post_json = post.model_dump(mode='json'),
            author_id = author_id,
        )
        res = await self.post_repository.create(post)
        await self.update_post_service.create_update_post(update_post)
        return res

    async def get_post(self, post_id: UUID) -> Post:
        post = await self.post_repository.get(post_id)

        file_path = self.upload_service.get_file_url(post.image_path)

        post.image_path = file_path
        return post

    async def update_post(self, post_id: UUID, post: UpdatePostDTO, author_id: UUID) -> Post:
        update_post = CreateUpdatePostDTO(
            post_id = post_id,
            post_json = post.model_dump(mode='json'),
            author_id = author_id,
        )
        res = await self.post_repository.update(post_id, post)
        await self.update_post_service.create_update_post(update_post)
        return res

    async def delete_post(self, post_id: UUID) -> None:
        return await self.post_repository.delete(post_id)
