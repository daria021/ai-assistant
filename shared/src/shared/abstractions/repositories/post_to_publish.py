from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.domain.dto import CreatePostToPublishDTO, UpdatePostToPublishDTO
from shared.domain.enums import PublicationStatus
from shared.domain.models import PostToPublish
from .uuid_pk_abstract import UUIDPKRepositoryInterface


class PostToPublishRepositoryInterface(
    UUIDPKRepositoryInterface[PostToPublish, CreatePostToPublishDTO, UpdatePostToPublishDTO],
    ABC,
):
    @abstractmethod
    async def get_queued_post(self) -> Optional[PostToPublish]:
        ...

    @abstractmethod
    async def set_status(self, post_id: UUID, status: PublicationStatus) -> None:
        ...

    @abstractmethod
    async def get_posts_by_manager(self, responsible_manager_id: UUID) -> list[PostToPublish]:
        ...

