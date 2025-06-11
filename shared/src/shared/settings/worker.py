from shared.domain.models.user import UserWithSessionString
from shared.settings import AbstractSettings


class WorkerSettings(AbstractSettings):
    user: UserWithSessionString
    api_id: int
    api_hash: str
