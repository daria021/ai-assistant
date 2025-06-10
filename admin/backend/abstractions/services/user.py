from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from shared.domain.dto import CreateUserDTO, UpdateUserDTO
from shared.domain.models import User


class UserServiceInterface(ABC):
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        ...

    @abstractmethod
    async def create_user(self, user: CreateUserDTO) -> UUID:
        ...

    @abstractmethod
    async def get_user(self, user_id: UUID) -> User:
        ...

    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        ...

    @abstractmethod
    async def update_user(self, user_id: UUID, user: UpdateUserDTO) -> None:
        ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def ensure_user(self, dto: CreateUserDTO) -> User:
        ...

    @abstractmethod
    async def send_auth_code(self, user_id: UUID, phone: str) -> None:
        ...

    @abstractmethod
    async def get_session_string_for_user(
            self,
            phone: str,
            code: str,
            user_id: UUID,
            password: Optional[str] = None,
    ) -> None:
        ...
