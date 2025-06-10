from pydantic import SecretStr
from shared.settings import AbstractSettings


class ServiceAccountSettings(AbstractSettings):
    api_id: int
    api_hash: str
    session_string: SecretStr
