from typing import Optional
from uuid import UUID

from .abstract import CreateDTO, UpdateDTO
from shared.domain.enums import UserRole


class CreateUserDTO(CreateDTO):
    telegram_id: int
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None
    telegram_last_name: Optional[str] = None
    telegram_language_code: Optional[str] = None

    role: UserRole

    session_string: Optional[str] = None
    assistant_enabled: bool


class UpdateUserDTO(UpdateDTO):
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None
    telegram_last_name: Optional[str] = None
    telegram_language_code: Optional[str] = None

    role: Optional[UserRole] = None

    session_string: Optional[str] = None
    assistant_enabled: Optional[bool] = None
