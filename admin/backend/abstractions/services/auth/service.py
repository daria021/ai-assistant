from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.responses.auth import AuthTokens


class AuthServiceInterface(ABC):
    @abstractmethod
    async def get_user_id_from_jwt(self, token: str) -> UUID:
        ...

    @abstractmethod
    async def create_token(self, init_data: str) -> AuthTokens:
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> AuthTokens:
        ...
