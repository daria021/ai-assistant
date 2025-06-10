from abc import ABC, abstractmethod


class PostingServiceInterface(ABC):
    @abstractmethod
    async def schedule_post(self, post):
        ...
