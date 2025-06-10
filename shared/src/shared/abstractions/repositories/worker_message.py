from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from shared.abstractions.repositories.uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto import CreateWorkerMessageDTO, UpdateWorkerMessageDTO
from shared.domain.enums import WorkerMessageStatus
from shared.domain.models import WorkerMessage


class WorkerMessageRepositoryInterface(
    UUIDPKRepositoryInterface[WorkerMessage, CreateWorkerMessageDTO, UpdateWorkerMessageDTO],
    ABC,
):
    @abstractmethod
    async def get_queued_message(self) -> Optional[WorkerMessage]:
        ...

    @abstractmethod
    async def set_message_status(
            self,
            message_id: UUID,
            status: WorkerMessageStatus,
            sent_at: Optional[datetime] = None
    ) -> None:
        ...

    @abstractmethod
    async def get_messages_from_same_request(self, message_id: UUID) -> list[WorkerMessage]:
        ...
