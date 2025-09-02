from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from sqlalchemy import select

from shared.abstractions.repositories import PostToPublishRepositoryInterface
from shared.domain.dto import CreatePostToPublishDTO, UpdatePostToPublishDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.enums import PublicationStatus
from shared.domain.models import (
    PostToPublish as PostToPublishModel,
    User as UserModel,
    Chat as ChatModel,
    Post as PostModel
)
from shared.infrastructure.main_db.entities import PostToPublish, User, Chat, Post
from .abstract import AbstractMainDBRepository


@dataclass
class PostToPublishRepository(
    AbstractMainDBRepository[PostToPublish, PostToPublishModel, CreatePostToPublishDTO, UpdatePostToPublishDTO],
    PostToPublishRepositoryInterface,
):
    joined_fields: dict[str, Optional[list[str]]] = field(default_factory=lambda: {
        "creator": None,
        "responsible_manager": None,
        "chats": None,
        "post": None,
    })
    _soft_delete: bool = field(default=True)


    async def get_all(self, limit: int = 1000, offset: int = 0, joined: bool = True) -> list[PostToPublishModel]:
        async with self.session_maker() as session:
            stmt = (
                select(self.entity)
                .where(self.entity.deleted_at.is_(None))
                .limit(limit)
                .offset(offset)
            )
            if joined and self.options:
                stmt = stmt.options(*self.options)

            if self._soft_delete:
                stmt = stmt.where(self.entity.deleted_at.is_(None))

            res = await session.execute(stmt)

            if self.options:
                res = res.unique()

            objs = res.scalars().all()

            return [self.entity_to_model(entity) for entity in objs]


    async def get_posts_by_manager(self, responsible_manager_id: UUID) -> list[PostToPublishModel]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(self.entity)
                .where(
                    self.entity.responsible_manager_id == responsible_manager_id,
                    self.entity.deleted_at.is_(None),
                )
                .options(*self.options)
            )

            posts = result.unique().scalars().all()

        return [self.entity_to_model(post) for post in posts]

    async def get_queued_post(self) -> Optional[PostToPublish]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(self.entity)
                .where(
                    self.entity.status == PublicationStatus.PENDING,
                    self.entity.deleted_at.is_(None),
                )
                .order_by(self.entity.created_at)
                .options(*self.options)
                .limit(1)
            )

            post = result.unique().scalars().one_or_none()

        return self.entity_to_model(post) if post else None

    async def set_status(self, post_id: UUID, status: PublicationStatus) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                post = await session.get(self.entity, post_id)
                post.status = status

    async def create(self, obj: CreatePostToPublishDTO) -> UUID:
        async with self.session_maker() as session:
            async with session.begin():
                chats = await session.execute(
                    select(Chat)
                    .where(Chat.id.in_(obj.chat_ids))
                )

                post = self.create_dto_to_entity(obj)
                post.chats = chats.scalars().all()
                session.add(post)

        return post.id

    def create_dto_to_entity(self, dto: CreatePostToPublishDTO) -> PostToPublish:
        return PostToPublish(
            id=dto.id,
            post_id=dto.post_id,
            creator_id=dto.creator_id,
            responsible_manager_id=dto.responsible_manager_id,
            scheduled_type=dto.scheduled_type,
            scheduled_date=dto.scheduled_date,
            scheduled_time=dto.scheduled_time,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )

    def entity_to_model(self, entity: PostToPublish) -> PostToPublishModel:
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
                responsible_manager_id=chat.responsible_manager_id,
                chat_type_id=chat.chat_type_id,
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

        return PostToPublishModel(
            id=entity.id,
            post_id=entity.post_id,
            creator_id=entity.creator_id,
            responsible_manager_id=entity.responsible_manager_id,
            scheduled_type=entity.scheduled_type,
            scheduled_date=entity.scheduled_date,
            scheduled_time=entity.scheduled_time,
            status=entity.status,
            creator=_map_user(entity.creator),
            responsible_manager=_map_user(entity.responsible_manager),
            chats=[_map_chat(x) for x in entity.chats],
            post=_map_post(entity.post),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
