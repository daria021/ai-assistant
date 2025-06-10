from abc import ABC, abstractmethod
from typing import Optional

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto import CreatePublishStoryRequestDTO, UpdatePublishStoryRequestDTO
from shared.domain.models import PublishStoryRequest


class PublishStoryRequestRepositoryInterface(
    UUIDPKRepositoryInterface[PublishStoryRequest, CreatePublishStoryRequestDTO, UpdatePublishStoryRequestDTO],
    ABC,
):
    @abstractmethod
    async def get_queued_message(self) -> Optional[PublishStoryRequest]:
        pass
