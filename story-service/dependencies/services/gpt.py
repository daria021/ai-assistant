from backend.abstractions.services.gpt import GPTServiceInterface
from backend.services import GPTService

def get_gpt_service() -> GPTServiceInterface:
    return GPTService()