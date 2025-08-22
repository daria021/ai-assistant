from dataclasses import dataclass
from uuid import UUID

from shared.abstractions.repositories.update_post import UpdatePostRepositoryInterface
from shared.domain.dto.update_post import CreateUpdatePostDTO, UpdateUpdatePostDTO

from abstractions.services.update_post import UpdatePostServiceInterface


@dataclass
class UpdatePostService(UpdatePostServiceInterface):
    update_post_repository: UpdatePostRepositoryInterface

    async def create_update_post(self, post: CreateUpdatePostDTO) -> UUID:
        return await self.update_post_repository.create(obj=post)
