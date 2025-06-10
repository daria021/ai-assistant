from backend.abstractions.services.mailing import MailingServiceInterface
from backend.dependencies.services.analytics_service import get_analytics_service_service
from backend.dependencies.services.bot import get_bot
from backend.dependencies.services.gpt import get_gpt_service
from backend.dependencies.services.user import get_user_service
from backend.services import MailingService


def get_mailing_service() -> MailingServiceInterface:
    return MailingService(
        bot=get_bot(),
        gpt=get_gpt_service(),
        user_service=get_user_service(),
        analytics_service_service=get_analytics_service_service()
    )
