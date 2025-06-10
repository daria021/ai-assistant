from abc import ABC, abstractmethod
from typing import Optional

from shared.domain.dto.post_to_publish import MessageEntityDTO


class TelegramMessagesRepositoryInterface(
    ABC,
):
    @abstractmethod
    async def send_message(
            self,
            chat_id: int,
            text: str,
            entities: Optional[list[MessageEntityDTO]] = None,
            media_path: Optional[str] = None,
            reply_to: Optional[int] = None,
    ) -> int:
        pass

    @abstractmethod
    async def join_chat(self, chat: str | int):
        ...
