from abc import ABC, abstractmethod
from uuid import UUID

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.models import Post
from sqlalchemy import select

class PostRepositoryInterface(
    UUIDPKRepositoryInterface[Post, CreatePostDTO, UpdatePostDTO],
    ABC,
):
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0, joined: bool = True) -> list[Post]:
        ...

    @abstractmethod
    async def update(self, obj_id: UUID, obj: UpdatePostDTO) -> Post:
        ...
