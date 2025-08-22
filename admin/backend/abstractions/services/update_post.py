from abc import ABC, abstractmethod

from shared.domain.dto.update_post import CreateUpdatePostDTO, UpdateUpdatePostDTO
from shared.domain.models.update_post import UpdatePost


class UpdatePostServiceInterface(ABC):

    @abstractmethod
    async def create_update_post(self, post: CreateUpdatePostDTO) -> UpdatePost:
        ...
