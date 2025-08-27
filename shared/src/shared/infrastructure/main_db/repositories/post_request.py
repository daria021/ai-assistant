from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from shared.abstractions.repositories import SendPostRequestRepositoryInterface
from shared.domain.dto import CreateSendPostRequestDTO, UpdateSendPostRequestDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.enums import SendPostRequestStatus
from shared.domain.models import (
    Chat as ChatModel,
    Post as PostModel,
    SendPostRequest as SendPostRequestModel,
    User as UserModel, SendingRequest,
)
from shared.infrastructure.main_db.entities import Chat, Post, SendPostRequest, User
from sqlalchemy import select

from .abstract import AbstractMainDBRepository


@dataclass
class SendPostRequestRepository(
    AbstractMainDBRepository[SendPostRequest, SendPostRequestModel, CreateSendPostRequestDTO, UpdateSendPostRequestDTO],
    SendPostRequestRepositoryInterface,
):
    joined_fields: dict[str, Optional[list[str]]] = field(default_factory=lambda: {
        "user": None,
        "chat": None,
        "post": None,
    })

    _soft_delete: bool = field(default=True)

    async def get_requests_from_same_publication(self, request_id: UUID) -> list[SendPostRequestModel]:
        async with self.session_maker() as session:
            request = await session.get(self.entity, request_id)
            if request.deleted_at is None:
                requests_result = await session.execute(
                    select(self.entity)
                    .where(self.entity.publication_id == request.publication_id,                     self.entity.deleted_at.is_(None),
                           self.entity.deleted_at.is_(None),)
                    .order_by(self.entity.created_at)
                    .options(*self.options)
                )
                requests = requests_result.unique().scalars().all()

        return [self.entity_to_model(request) for request in requests]

    async def get_queued_message(self) -> Optional[SendPostRequest]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(self.entity)
                .where(self.entity.status == SendPostRequestStatus.PLANNED, self.entity.deleted_at == None)
                .order_by(self.entity.created_at)
                .options(*self.options)
                .limit(1)
            )  # todo: batching?

            message = result.unique().scalars().one_or_none()

        return self.entity_to_model(message) if message else None

    def create_dto_to_entity(self, dto: CreateSendPostRequestDTO) -> SendPostRequest:
        return SendPostRequest(
            id=dto.id,
            post_id=dto.post_id,
            chat_id=dto.chat_id,
            user_id=dto.user_id,
            scheduled_at=dto.scheduled_at,
            publication_id=dto.publication_id,
            status=dto.status,
            sent_at=dto.sent_at,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: SendPostRequest) -> SendPostRequest:
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

        def _map_chat(chat: Chat) -> ChatModel:
            return ChatModel(
                id=chat.id,
                chat_id=chat.chat_id,
                name=chat.name,
                chat_type_id=chat.chat_type_id,
                responsible_manager_id=chat.responsible_manager_id,
                invite_link=chat.invite_link,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
            )

        def _map_post(post: Post) -> PostModel:
            return PostModel(
                id=post.id,
                text=post.text,
                name=post.name,
                is_template=post.is_template,
                html=post.html,
                entities=[MessageEntityDTO.model_validate(x) for x in post.entities] if post.entities else None,
                image_path=post.image_path,
                created_at=post.created_at,
                updated_at=post.updated_at,
            )

        return SendPostRequestModel(
            id=entity.id,
            post_id=entity.post_id,
            chat_id=entity.chat_id,
            user_id=entity.user_id,
            scheduled_at=entity.scheduled_at,
            status=entity.status,
            sent_at=entity.sent_at,
            publication_id=entity.publication_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            user=_map_user(entity.user),
            chat=_map_chat(entity.chat),
            post=_map_post(entity.post),
        )
