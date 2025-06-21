from typing import Optional
from uuid import UUID

from shared.domain.enums import UserRole
from .abstract import Model
from .proxy import Proxy


class User(Model):
    telegram_id: int
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None
    telegram_last_name: Optional[str] = None
    telegram_language_code: Optional[str] = None

    role: UserRole
    is_banned: Optional[bool] = False

    session_string: Optional[str] = None
    proxy_id: Optional[UUID] = None

    proxy: Optional[Proxy] = None

    assistant_enabled: bool


class UserWithSessionString(User):
    session_string: str
