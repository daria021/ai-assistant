from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID

from shared.abstractions.repositories import UserRepositoryInterface
from shared.domain.dto import CreateUserDTO, UpdateUserDTO
from shared.domain.enums import UserRole
from shared.domain.models import User as UserModel, Proxy as ProxyModel
from shared.infrastructure.main_db.entities import User, Proxy
from sqlalchemy import select, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from .abstract import AbstractMainDBRepository
from .exceptions import ProxyIsUnavailable, NoResultFoundException


@dataclass
class UserRepository(
    AbstractMainDBRepository[User, UserModel, CreateUserDTO, UpdateUserDTO],
    UserRepositoryInterface,
):
    joined_fields: dict[str, Optional[List[str]]] = field(
        default_factory=lambda: {
            "proxy": None,
            "chats": None,
        },
    )

    async def set_proxy(self, user_id: UUID, proxy_id: UUID) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                proxy = await session.get(Proxy, proxy_id, options=[joinedload(Proxy.user)])
                if proxy is None:
                    raise NoResultFoundException(f"Proxy {proxy_id} not found")

                if not proxy.is_free:
                    raise ProxyIsUnavailable(f"Proxy {proxy.id} is in use by user {proxy.user.id}")

                proxy.is_free = False

                user = await session.get(self.entity, user_id)
                user.proxy_id = proxy_id

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            async with self.session_maker() as session:
                if self.options:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.telegram_username == username)
                        .options(*self.options)
                    )
                    user = res.unique().scalars().one()
                else:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.telegram_username == username)
                    )
                    user = res.scalars().one()
        except NoResultFound:
            return None

        return self.entity_to_model(user)

    async def get_managers(self) -> List[User]:
        async with self.session_maker() as session:
            stmt = select(self.entity).where(
                or_(
                    self.entity.role == UserRole.MANAGER,
                    self.entity.role == UserRole.PUBLICATIONS_MANAGER
                )
            )
            if self.options:
                stmt = stmt.options(*self.options)

            res = (await session.execute(stmt)).unique().scalars().all()

        return [self.entity_to_model(x) for x in res] if res else []

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        try:
            async with self.session_maker() as session:
                if self.options:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.telegram_id == telegram_id)
                        .options(*self.options)
                    )
                    user = res.unique().scalars().one()
                else:
                    res = await session.execute(
                        select(self.entity)
                        .where(self.entity.telegram_id == telegram_id)
                    )
                    user = res.scalars().one()

        except NoResultFound:
            return None

        return self.entity_to_model(user)

    def create_dto_to_entity(self, dto: CreateUserDTO) -> User:
        return User(
            id=dto.id,
            telegram_id=dto.telegram_id,
            telegram_username=dto.telegram_username,
            telegram_last_name=dto.telegram_last_name,
            telegram_first_name=dto.telegram_first_name,
            telegram_language_code=dto.telegram_language_code,
            role=dto.role,
            assistant_enabled=dto.assistant_enabled,
            session_string=dto.session_string,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: User) -> User:
        def _map_proxy(proxy: Proxy) -> ProxyModel:
            return ProxyModel(
                id=proxy.id,
                proxy_string=proxy.proxy_string,
                is_free=proxy.is_free,
                is_deprecated=proxy.is_deprecated,
                created_at=proxy.created_at,
                updated_at=proxy.updated_at,
            )

        return UserModel(
            id=entity.id,
            telegram_id=entity.telegram_id,
            telegram_username=entity.telegram_username,
            telegram_last_name=entity.telegram_last_name,
            telegram_first_name=entity.telegram_first_name,
            telegram_language_code=entity.telegram_language_code,
            role=entity.role,
            is_banned=entity.is_banned,
            assistant_enabled=entity.assistant_enabled,
            session_string=entity.session_string,
            proxy_id=entity.proxy_id,
            proxy=_map_proxy(entity.proxy) if entity.proxy else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
