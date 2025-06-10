from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select

from shared.abstractions.repositories.worker_message import WorkerMessageRepositoryInterface
from shared.domain.dto import CreateWorkerMessageDTO, UpdateWorkerMessageDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.enums import WorkerMessageStatus
from shared.domain.models import (
    User as UserModel,
)
from shared.domain.models import WorkerMessage as WorkerMessageModel
from shared.infrastructure.main_db.entities import User, WorkerMessage
from .abstract import AbstractMainDBRepository


@dataclass
class WorkerMessageRepository(
    AbstractMainDBRepository[WorkerMessage, WorkerMessageModel, CreateWorkerMessageDTO, UpdateWorkerMessageDTO],
    WorkerMessageRepositoryInterface,
):
    joined_fields: dict[str, Optional[list[str]]] = field(default_factory=lambda: {
        "user": None,
    })

    async def get_messages_from_same_request(self, message_id: UUID) -> list[WorkerMessage]:
        async with self.session_maker() as session:
            message = await session.get(self.entity, message_id)
            messages_result = await session.execute(
                select(self.entity)
                .where(self.entity.request_id == message.request_id)
                .order_by(self.entity.created_at)
                .options(*self.options)
            )
            messages = messages_result.unique().scalars().all()

        return [self.entity_to_model(message) for message in messages]

    async def get_queued_message(self) -> Optional[WorkerMessageModel]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(self.entity)
                .where(self.entity.status == WorkerMessageStatus.PENDING)
                .order_by(self.entity.created_at)
                .options(*self.options)
                .limit(1)
            )  # todo: batching?

            message = result.unique().scalars().one_or_none()

        return self.entity_to_model(message) if message else None

    async def set_message_status(
            self,
            message_id: UUID,
            status: WorkerMessageStatus,
            sent_at: Optional[datetime] = None
    ) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                message = await session.get(self.entity, message_id)
                message.status = status
                if sent_at:
                    message.sent_at = sent_at

    def entity_to_model(self, entity: WorkerMessage) -> WorkerMessageModel:
        def _map_user(user: User) -> UserModel:
            return UserModel(
                id=user.id,
                telegram_id=user.telegram_id,
                telegram_username=user.telegram_username,
                telegram_last_name=user.telegram_last_name,
                telegram_first_name=user.telegram_first_name,
                telegram_language_code=user.telegram_language_code,
                role=user.role,
                assistant_enabled=user.assistant_enabled,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

        return WorkerMessageModel(
            id=entity.id,
            user_id=entity.user_id,
            type=entity.type,
            text=entity.text,
            entities=[MessageEntityDTO.model_validate(x) for x in entity.entities] if entity.entities else None,
            media_path=entity.media_path,
            status=entity.status,
            sent_at=entity.sent_at,
            request_id=entity.request_id,
            chat_id=entity.chat_id,
            user=_map_user(entity.user),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def create_dto_to_entity(self, dto: CreateWorkerMessageDTO) -> WorkerMessage:
        return WorkerMessage(
            id=dto.id,
            user_id=dto.user_id,
            chat_id=dto.chat_id,
            type=dto.type,
            text=dto.text,
            entities=[x.model_dump(mode='json') for x in dto.entities] if dto.entities else None,
            media_path=dto.media_path,
            status=dto.status,
            sent_at=dto.sent_at,
            request_id=dto.request_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
