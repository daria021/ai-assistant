from pydantic import ConfigDict

from .abstract import Model
from ...infrastructure.enums.user_status import UserStatus


class User(Model):
    telegram_id: int
    nickname: str
    status: UserStatus

    model_config = ConfigDict(from_attributes=True)
