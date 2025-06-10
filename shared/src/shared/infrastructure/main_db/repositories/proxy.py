from dataclasses import dataclass, field
from typing import Optional, List

from sqlalchemy import select, func

from shared.abstractions.repositories import ProxyRepositoryInterface
from shared.domain.dto import CreateProxyDTO, UpdateProxyDTO
from shared.domain.models import Proxy as ProxyModel, User as UserModel
from shared.infrastructure.main_db.entities import Proxy, User
from .abstract import AbstractMainDBRepository
from .exceptions import NoFreeProxiesException


@dataclass
class ProxyRepository(
    AbstractMainDBRepository[Proxy, ProxyModel, CreateProxyDTO, UpdateProxyDTO],
    ProxyRepositoryInterface,
):
    # joined_fields: dict[str, Optional[List[str]]] = field(
    #     default_factory=lambda: {
    #         'user': None,
    #     },
    # )

    async def get_available_proxies_count(self) -> int:
        async with self.session_maker() as session:  # session: AsyncSession
            result = await session.execute(
                select(func.count(self.entity.id))
                .where(
                    self.entity.is_free == True,
                    self.entity.is_deprecated == False,
                )
            )
            return result.scalar()

    async def get_available_proxy(self) -> ProxyModel:
        async with self.session_maker() as session:
            result = await session.execute(
                select(self.entity)
                .where(
                    self.entity.is_free == True,
                    self.entity.is_deprecated == False,
                )
                .order_by(self.entity.created_at)
                .limit(1)
            )

            result = result.scalars().one_or_none()
            if result is None:
                raise NoFreeProxiesException

        return self.entity_to_model(result)

    def create_dto_to_entity(self, dto: CreateProxyDTO) -> Proxy:
        return Proxy(
            id=dto.id,
            proxy_string=dto.proxy_string,
            is_free=dto.is_free,
            is_deprecated=dto.is_deprecated,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Proxy) -> ProxyModel:
        def _map_user(user: User) -> UserModel:
            return None  # noqa

        return ProxyModel(
            id=entity.id,
            proxy_string=entity.proxy_string,
            is_free=entity.is_free,
            is_deprecated=entity.is_deprecated,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
