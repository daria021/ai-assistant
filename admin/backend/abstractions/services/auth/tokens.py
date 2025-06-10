import logging
from abc import ABC, abstractmethod

from domain.responses.auth import AuthTokens

logger = logging.getLogger(__name__)


class TokenServiceInterface(ABC):
    @abstractmethod
    def get_token_payload(self, token: str) -> dict:
        ...

    @abstractmethod
    def create_auth_token(self, user_id: str) -> AuthTokens:
        ...
