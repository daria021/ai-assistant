from dataclasses import dataclass
from typing import List
from uuid import UUID

from backend.abstractions.repositories import UserRepositoryInterface
from backend.abstractions.services.user import UserServiceInterface
from domain.dto.user import CreateUserDTO
from domain.models.user import User


@dataclass
class UserService(UserServiceInterface):
    user_repository: UserRepositoryInterface

    async def get_all_users(self) -> List[User]:
        return await self.user_repository.get_all()

    async def get_user(self, user_id: UUID) -> User:
        return await self.user_repository.get(user_id)

    async def create_user(self, user: CreateUserDTO) -> None:
        return await self.user_repository.create(user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        return await self.user_repository.get_by_telegram_id(telegram_id)