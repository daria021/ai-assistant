from abc import ABC, abstractmethod
from uuid import UUID


class CRUDRepositoryInterface[Model, CreateDTO, UpdateDTO](ABC):
    @abstractmethod
    async def create(self, obj: CreateDTO) -> None:
        ...

    @abstractmethod
    async def get(self, obj_id: UUID) -> Model:
        ...

    @abstractmethod
    async def update(self, obj_id: UUID, obj: UpdateDTO) -> None:
        ...

    @abstractmethod
    async def delete(self, obj_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Model]:
        ...
