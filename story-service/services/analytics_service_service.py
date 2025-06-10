from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from backend.abstractions.repositories import AnalyticsServiceRepositoryInterface
from backend.abstractions.services.analytics_service import AnalyticsServiceServiceInterface
from domain.dto.analytics_service import UpdateServiceDTO
from domain.models.analytics_service import Service

@dataclass
class AnalyticsServiceService(AnalyticsServiceServiceInterface):
    service_repository: AnalyticsServiceRepositoryInterface
    
    async def get_all_services(self) -> List[Service]:
        return await self.service_repository.get_all()

    async def get_available_services(self) -> Optional[List[Service]]:
        return await self.service_repository.get_available_services()

    async def update_service_active_status(self, svc_id: UUID, new_status: bool) -> None:
        update_model = UpdateServiceDTO(
            is_active=new_status,
        )
        return await self.service_repository.update(svc_id, update_model)
