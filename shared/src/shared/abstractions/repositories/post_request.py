from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto.post_request import CreateSendPostRequestDTO, UpdateSendPostRequestDTO
from shared.domain.models.post_request import SendPostRequest


class SendPostRequestRepositoryInterface(
    UUIDPKRepositoryInterface[SendPostRequest, CreateSendPostRequestDTO, UpdateSendPostRequestDTO],
    ABC,
):
    @abstractmethod
    async def get_queued_message(self) -> Optional[SendPostRequest]:
        pass

    @abstractmethod
    async def get_requests_from_same_publication(self, request_id: UUID) -> list[SendPostRequest]:
        ...
