from typing import Optional
from abc import ABC, abstractmethod
from uuid import UUID

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto import CreateUserDTO, UpdateUserDTO
from shared.domain.models import User


class UserRepositoryInterface(
    UUIDPKRepositoryInterface[User, CreateUserDTO, UpdateUserDTO],
    ABC,
):
    @abstractmethod
    async def get_by_username(self, username: str) -> User:
        ...

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        ...

    @abstractmethod
    async def set_proxy(self, user_id: UUID, proxy_id: UUID) -> None:
        ...
