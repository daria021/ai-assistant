import hashlib
import hmac
import logging
import time
import json
from typing import Optional
from urllib.parse import parse_qs
from dataclasses import dataclass
from uuid import UUID

from shared.domain.dto import CreateUserDTO
from shared.domain.enums import UserRole
from shared.infrastructure.sqlalchemy import NotFoundException

from abstractions.services.auth.service import AuthServiceInterface
from abstractions.services.auth.tokens import TokenServiceInterface
from abstractions.services.user import UserServiceInterface
from domain.responses.auth import AuthTokens
from services.auth.exceptions import ExpiredDataException, InvalidTokenException
from services.exceptions import BannedUserException

logger = logging.getLogger(__name__)


@dataclass
class AuthService(AuthServiceInterface):
    bot_token: str
    token_service: TokenServiceInterface
    user_service: UserServiceInterface

    async def get_user_id_from_jwt(self, token: str) -> UUID:
        try:
            payload = self.token_service.get_token_payload(token=token)
            user_id: str | None = payload.get('sub', None)
            if not user_id:
                raise InvalidTokenException()

            user = await self.user_service.get_user(UUID(user_id))  # todo: pk type

            return user.id
        except (InvalidTokenException, NotFoundException):
            raise

    async def create_token(self, init_data: str) -> AuthTokens:
        """Verifies Telegram Mini App auth data properly."""
        # Parse initData properly (decode URL params)
        data_dict = {k: v[0] for k, v in parse_qs(init_data).items()}

        # Extract hash separately
        received_hash = data_dict.pop("hash", None)
        if not received_hash:
            raise InvalidTokenException("Missing hash in init data")

        # Check expiration
        auth_date = int(data_dict.get("auth_date", "0"))
        if time.time() - auth_date > 86400:  # Expire after 1 day
            raise ExpiredDataException()

        # Step 1: Sort the key-value pairs in alphabetical order
        sorted_data_string = "\n".join(f"{k}={v}" for k, v in sorted(data_dict.items()))

        # Step 2: Create HMAC-SHA256 signature of the bot token using 'WebAppData' as key
        secret_key = hmac.new(b"WebAppData", self.bot_token.encode(), hashlib.sha256).digest()

        # Step 3: Create final HMAC-SHA256 signature using the previous step result as the key
        computed_hash = hmac.new(secret_key, sorted_data_string.encode(), hashlib.sha256).hexdigest()

        logger.info(f"Computed Hash: {computed_hash}, Received Hash: {received_hash}, InitData: {init_data}")

        # Step 4: Validate hash
        if computed_hash != received_hash:
            raise InvalidTokenException("Invalid init data hash")

        # Extract Telegram User ID
        user_data = json.loads(data_dict.get("user", "{}"))
        telegram_user_id = int(user_data.get("id", 0))
        username = user_data.get("username", None)
        first_name = user_data.get("first_name", None)
        last_name = user_data.get("last_name", None)
        language_code = user_data.get("language_code", None)

        # Ensure user exists
        user_dto = CreateUserDTO(
            telegram_id=telegram_user_id,
            telegram_username=username,
            telegram_first_name=first_name,
            telegram_last_name=last_name,
            telegram_language_code=language_code,
            role=UserRole.MANAGER,
            assistant_enabled=False,
        )
        user = await self.user_service.ensure_user(user_dto)

        # Generate access & refresh tokens
        return self.token_service.create_auth_token(user_id=str(user.id))

    async def refresh_token(self, refresh_token: str) -> AuthTokens:
        try:
            old_claims = self.token_service.get_token_payload(refresh_token)
            user_id = old_claims['sub']
            await self.user_service.get_user(user_id)

            return self.token_service.create_auth_token(user_id)
        except (InvalidTokenException, NotFoundException):
            raise
