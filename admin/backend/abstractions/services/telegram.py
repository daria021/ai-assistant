from abc import ABC, abstractmethod
from typing import Optional

from domain.models.chat import TelegramChatInfo


class TelegramServiceInterface(ABC):
    @abstractmethod
    async def get_chat_info(self, invite_link: str) -> TelegramChatInfo:
        ...

    @abstractmethod
    async def send_auth_code(self, phone: str, proxy: Optional[str] = None) -> None:
        ...

    @abstractmethod
    async def get_session_string(
            self,
            phone: str,
            code: str,
            proxy: Optional[str] = None,
            password: Optional[str] = None,
    ) -> str:
        ...
