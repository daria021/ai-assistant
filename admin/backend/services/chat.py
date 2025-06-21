import logging
import re
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from shared.abstractions.repositories import ChatRepositoryInterface
from shared.domain.dto import CreateChatDTO, UpdateChatDTO
from shared.domain.models import Chat

from abstractions.services.chat import ChatServiceInterface
from abstractions.services.telegram import TelegramServiceInterface
from services.exceptions import InvalidInviteLinkError, ChatAlreadyExistsError

logger = logging.getLogger(__name__)


@dataclass
class ChatService(ChatServiceInterface):
    chats_repository: ChatRepositoryInterface
    telegram_service: TelegramServiceInterface

    async def get_chats(self) -> list[Chat]:
        return await self.chats_repository.get_all()

    async def update_chat(self, chat_id: UUID, chat: UpdateChatDTO) -> Chat:
        return await self.chats_repository.update(chat_id, chat)

    async def get_chats_by_type(self, type_id: UUID) -> list[Chat]:
        return await self.chats_repository.get_by_type(type_id)

    async def create_chat_by_link(
            self,
            invite_link: str,
            manager_id: UUID,
            type_id: Optional[UUID] = None,
    ) -> Chat:
        """
        Проверяет invite_link, запрашивает у репозитория дубликаты,
        резолвит информацию о чате и сохраняет новую запись.
        """
        link = invite_link.strip()

        # 1. Базовая валидация формата ссылки
        pattern = r"^(https?://)?t\.me/[\w\-\+]+$"
        if not re.match(pattern, link):
            raise InvalidInviteLinkError(f"Неверный формат invite_link: {link}")

        # 2. Проверяем, что такого чата ещё нет
        existing = await self.chats_repository.get_by_invite_link(link)
        if existing:
            raise ChatAlreadyExistsError(f"Чат уже зарегистрирован: {link}")

        # 3. Получаем информацию о чате из тг
        chat_info = await self.telegram_service.get_chat_info(invite_link)

        # 4. Собираем доменную модель и сохраняем
        new_chat = CreateChatDTO(
            name=chat_info.title,
            chat_id=int(chat_info.id),
            invite_link=link,
            chat_type_id=type_id,
            responsible_manager_id=manager_id,
        )
        new_chat_id = await self.chats_repository.create(new_chat)
        return await self.chats_repository.get(new_chat_id)
