from abc import ABC, abstractmethod

from shared.domain.models import Chat


class ChatServiceInterface(ABC):
    @abstractmethod
    async def get_chats(self) -> list[Chat]:
        ...

    @abstractmethod
    async def create_chat_by_link(self, invite_link: str) -> Chat:
        ...
