from abstractions.services.bot_service import BotServiceInterface
from services.bot_service import AiogramBotService

def get_bot_service() -> BotServiceInterface:
    return AiogramBotService()
