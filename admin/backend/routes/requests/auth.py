from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TelegramAuthRequest(BaseModel):
    initData: str
    ref: Optional[UUID] = None
