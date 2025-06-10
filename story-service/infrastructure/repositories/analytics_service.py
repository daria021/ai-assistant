import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy import select

from backend.abstractions.repositories import AnalyticsServiceRepositoryInterface
from infrastructure.repositories.sqlalchemy import AbstractSQLAlchemyRepository
from domain.dto.analytics_service import CreateServiceDTO, UpdateServiceDTO
from domain.models.analytics_service import Service as ServiceModel
from infrastructure.entities import Service

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsServiceRepository(
    AbstractSQLAlchemyRepository[Service, ServiceModel, CreateServiceDTO, UpdateServiceDTO],
    AnalyticsServiceRepositoryInterface,
):

    async def get_available_services(self) -> List[ServiceModel]:
        async with self.session_maker() as session:
            services = await session.execute(select(self.entity).where(self.entity.is_active))

        services = services.scalars().all()
        return [self.entity_to_model(service) for service in services]

    def create_dto_to_entity(self, dto: CreateServiceDTO) -> Service:
        return Service(
            id=dto.id,
            name=dto.name,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Service) -> ServiceModel:
        return ServiceModel(
            id=entity.id,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
