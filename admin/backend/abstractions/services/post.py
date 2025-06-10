from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.models import post


class PostServiceInterface(ABC):

    @abstractmethod
    async def get_all_posts(self) -> List[post]:
        ...

    @abstractmethod
    async def create_post(self, post: CreatePostDTO) -> UUID:
        ...

    @abstractmethod
    async def get_post(self, post_id: UUID) -> post:
        ...

    @abstractmethod
    async def update_post(self, post_id: UUID, post: UpdatePostDTO) -> None:
        ...

    @abstractmethod
    async def delete_post(self, post_id: UUID) -> None:
        ...
