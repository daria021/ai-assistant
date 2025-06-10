from abc import ABC
from typing import List
from uuid import UUID

from domain.dto.user import CreateUserDTO
from domain.models.user import User


class UserServiceInterface(ABC):
    async def get_all_users(self) -> List[User]:
        ...

    async def create_user(self, user: CreateUserDTO) -> None:
        ...

    async def get_user(self, user_id: UUID) -> User:
        ...

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        ...
