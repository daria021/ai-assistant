from typing import Optional

from infrastructure.entities import Story
from infrastructure.enums.user_status import UserStatus
from domain.dto.base import CreateDTO, UpdateDTO


class CreateUserDTO(CreateDTO):
    telegram_id: int
    nickname: Optional[str]
    status: UserStatus
    session_string: str
    stories: list[Story]


class UpdateUserDTO(UpdateDTO):
    telegram_id: Optional[int]
    nickname: Optional[str]
    status: Optional[UserStatus]
    session_string: Optional[str]
    stories: list[Story]
