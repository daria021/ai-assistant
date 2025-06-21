import logging
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from shared.abstractions.repositories import UserRepositoryInterface, ProxyRepositoryInterface
from shared.domain.dto import CreateUserDTO, UpdateUserDTO
from shared.domain.models import User
from shared.infrastructure.main_db import NoFreeProxiesException

from abstractions.services.telegram import TelegramServiceInterface
from abstractions.services.user import UserServiceInterface
from services.exceptions import UserHasNoProxyException

logger = logging.getLogger(__name__)

@dataclass
class UserService(UserServiceInterface):
    user_repository: UserRepositoryInterface
    telegram_service: TelegramServiceInterface
    proxy_repository: ProxyRepositoryInterface

    async def get_all_users(self) -> List[User]:
        return await self.user_repository.get_all()

    async def get_managers(self) -> List[User]:
        return await self.user_repository.get_managers()

    async def create_user(self, user: CreateUserDTO) -> UUID:
        return await self.user_repository.create(user)

    async def get_user(self, user_id: UUID) -> User:
        return await self.user_repository.get(user_id)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        return await self.user_repository.get_by_telegram_id(telegram_id)

    async def update_user(self, user_id: UUID, user: UpdateUserDTO) -> User:
        return await self.user_repository.update(user_id, user)

    async def delete_user(self, user_id: UUID) -> None:
        return await self.user_repository.delete(user_id)

    async def ensure_user(self, dto: CreateUserDTO) -> User:
        logger.info(f"Ensuring user {dto.telegram_id}")
        user = await self.user_repository.get_by_telegram_id(dto.telegram_id)
        logger.info(f"User {dto.telegram_id} is {user}")
        if not user:
            user_id = await self.create_user(dto)
            user = await self.user_repository.get(user_id)
            logger.info(f"User {dto.telegram_id} was created just now")

        return user

    async def send_auth_code(self, user_id: UUID, phone: str) -> None:
        try:
            proxy = await self.proxy_repository.get_available_proxy()
        except NoFreeProxiesException:
            logger.error(f"No free proxies available")
            raise NoFreeProxiesException

        await self.user_repository.set_proxy(user_id, proxy.id)
        await self.telegram_service.send_auth_code(phone, proxy=proxy.proxy_string)

    async def get_session_string_for_user(
            self,
            phone: str,
            code: str,
            user_id: UUID,
            password: Optional[str] = None,
    ) -> None:
        user = await self.user_repository.get(user_id)
        if not user.proxy:
            raise UserHasNoProxyException(f"User {user_id} has no connected proxy")

        session_string = await self.telegram_service.get_session_string(
            phone=phone,
            code=code,
            proxy=user.proxy.proxy_string,
            password=password,
        )
        update_dto = UpdateUserDTO(
            session_string=session_string,
        )

        await self.update_user(user_id, update_dto)

