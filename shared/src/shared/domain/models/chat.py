from typing import Optional
from uuid import UUID

from .abstract import Model


class Chat(Model):
    chat_type_id: Optional[UUID] = None
    name: str
    chat_id: int
    invite_link: Optional[str] = None
    responsible_manager_id: UUID
