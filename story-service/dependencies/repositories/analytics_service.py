from backend.abstractions.repositories import AnalyticsServiceRepositoryInterface
from backend.dependencies.repositories.session_maker import get_session_maker
from infrastructure.repositories.analytics_service import AnalyticsServiceRepository


def get_analytics_service_repository() -> AnalyticsServiceRepositoryInterface:
    return AnalyticsServiceRepository(
        session_maker=get_session_maker()
    )