from abc import ABC, abstractmethod
from typing import NoReturn, Any


class ConsumerInterface[ExecutableServiceInterface: Any](ABC):
    @abstractmethod
    async def execute(self) -> NoReturn:
        ...
