from abc import ABC
from typing import List, Optional
from uuid import UUID

from shared.domain.models.analytics_service import Service


class AnalyticsServiceServiceInterface(ABC):

    async def get_all_services(self) -> List[Service]:
        ...

    async def get_available_services(self) -> Optional[List[Service]]:
        ...

    async def update_service_active_status(self, svc_id: UUID, new_status: bool) -> None:
        ...
