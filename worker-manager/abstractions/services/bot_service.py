from abc import ABC, abstractmethod

class BotServiceInterface(ABC):
    @abstractmethod
    async def send_post(
        self,
        chat_id: int,
        text: str,
        entities: list = None,
        media_path: str = None,
    ) -> None:
        ...
