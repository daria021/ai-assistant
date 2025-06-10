from abc import ABC
from typing import List

from backend.abstractions.repositories import CRUDRepositoryInterface
from domain.dto.analytics_service import CreateServiceDTO, UpdateServiceDTO
from domain.models.analytics_service import Service


class AnalyticsServiceRepositoryInterface(
    CRUDRepositoryInterface[Service, CreateServiceDTO, UpdateServiceDTO],
    ABC,
):

    def entity_to_model(self, entity: Service) -> Service:
        ...

    def create_dto_to_entity(self, dto: CreateServiceDTO) -> Service:
        ...

    async def get_available_services(self) -> List[Service]:
        ...

