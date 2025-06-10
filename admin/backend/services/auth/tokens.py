import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC

from jwt import (
    decode, encode,
    ExpiredSignatureError as ExpiredSignatureJWTError,
    InvalidTokenError as InvalidTokenJWTError
)

from abstractions.services.auth.tokens import TokenServiceInterface
from domain.responses.auth import AuthTokens
from services.auth.exceptions import InvalidTokenException, ExpiredTokenException
from shared.settings import JwtSettings

logger = logging.getLogger(__name__)


@dataclass
class TokenService(TokenServiceInterface):
    jwt_settings: JwtSettings

    def create_auth_token(self, user_id: str) -> AuthTokens:
        access_claims = {
            'sub': user_id,
            'exp': datetime.now(tz=UTC) + timedelta(seconds=self.jwt_settings.access_expire),
        }

        refresh_claims = {
            'sub': user_id,
            'exp': datetime.now(tz=UTC) + timedelta(seconds=self.jwt_settings.refresh_expire),
        }

        return AuthTokens(
            access_token=self._create_token(**access_claims),
            refresh_token=self._create_token(**refresh_claims),
        )

    def _create_token(self, **claims) -> str:
        if 'iss' not in claims:
            claims["iss"] = self.jwt_settings.issuer

        if 'aud' not in claims:
            claims["aud"] = self.jwt_settings.audience

        token = encode(
            payload=claims,
            key=self.jwt_settings.secret_key.get_secret_value(),
            algorithm="HS256"
        )

        return token

    def get_token_payload(self, token: str) -> dict:
        try:
            claims = decode(
                token,
                self.jwt_settings.secret_key.get_secret_value(),
                algorithms=["HS256"],
                issuer=self.jwt_settings.issuer,
                audience=self.jwt_settings.audience,
                options={
                    "verify_exp": True
                },
            )

            return claims
        except ExpiredSignatureJWTError as ex:
            logger.error("Token has expired: %s", token)
            raise ExpiredTokenException from ex
        except InvalidTokenJWTError as ex:
            logger.error("Invalid token: %s. Error: %s", token, ex)
            raise InvalidTokenException from ex
