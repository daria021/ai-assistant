from backend.abstractions.services.analytics_service import AnalyticsServiceServiceInterface
from backend.dependencies.repositories.analytics_service import get_analytics_service_repository
from backend.services.analytics_service_service import AnalyticsServiceService


def get_analytics_service_service() -> AnalyticsServiceServiceInterface:
    return AnalyticsServiceService(
        service_repository=get_analytics_service_repository()
    )