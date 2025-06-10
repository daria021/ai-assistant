from abc import ABC

from abstractions.repositories import CRUDRepositoryInterface
from domain.dto.user import CreateUserDTO, UpdateUserDTO
from domain.models.user import User


class UserRepositoryInterface(
    CRUDRepositoryInterface[User, CreateUserDTO, UpdateUserDTO],
    ABC,
):
    async def get_by_telegram_id(self, telegram_id: int) -> User:
        ...
