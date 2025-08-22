from abc import ABC, abstractmethod


class CRUDRepositoryInterface[PK_TYPE, Model, CreateDTO, UpdateDTO](ABC):
    @abstractmethod
    async def create(self, obj: CreateDTO) -> PK_TYPE:
        pass

    @abstractmethod
    async def get(self, obj_id: PK_TYPE) -> Model:
        pass

    @abstractmethod
    async def update(self, obj_id: PK_TYPE, obj: UpdateDTO) -> Model:
        pass

    @abstractmethod
    async def delete(self, obj_id: PK_TYPE) -> None:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Model]:
        pass


class UOWInterface(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def attach(self, *repositories: CRUDRepositoryInterface) -> None:
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
