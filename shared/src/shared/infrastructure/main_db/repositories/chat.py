from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from shared.abstractions.repositories import ChatRepositoryInterface
from shared.domain.dto import CreateChatDTO, UpdateChatDTO
from shared.domain.models import Chat as ChatModel
from shared.infrastructure.main_db.entities import Chat
from .abstract import AbstractMainDBRepository


@dataclass
class ChatRepository(
    AbstractMainDBRepository[Chat, ChatModel, CreateChatDTO, UpdateChatDTO],
    ChatRepositoryInterface,
):
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Chat]:
        try:
            async with self.session_maker() as session:
                if self.options:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.telegram_id == telegram_id)
                        .options(*self.options)
                    )
                    chat = res.unique().scalars().one()
                else:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.telegram_id == telegram_id)
                    )
                    chat = res.scalars().one()

        except NoResultFound:
            return None

        return self.entity_to_model(chat)

    async def get_by_invite_link(self, invite_link: str) -> Chat:
        try:
            async with self.session_maker() as session:
                if self.options:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.invite_link == invite_link)
                        .options(*self.options)
                    )
                    chat = res.unique().scalars().one()
                else:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.invite_link == invite_link)
                    )
                    chat = res.scalars().one()

        except NoResultFound:
            return None

        return self.entity_to_model(chat)


    def create_dto_to_entity(self, dto: CreateChatDTO) -> Chat:
        return Chat(
            id=dto.id,
            invite_link=dto.invite_link,
            chat_id=dto.chat_id,
            name=dto.name,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Chat) -> Chat:
        return ChatModel(
            id=entity.id,
            invite_link=entity.invite_link,
            chat_id=entity.chat_id,
            name=entity.name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
