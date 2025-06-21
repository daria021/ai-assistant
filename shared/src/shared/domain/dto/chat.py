from typing import Optional
from uuid import UUID

from .abstract import CreateDTO, UpdateDTO


class CreateChatDTO(CreateDTO):
    chat_type_id: UUID
    name: str
    chat_id: int
    invite_link: Optional[str] = None
    responsible_manager_id: UUID


class UpdateChatDTO(UpdateDTO):
    chat_type_id: Optional[UUID] = None
    name: Optional[str] = None
    chat_id: Optional[int] = None
    invite_link: Optional[str] = None
    responsible_manager_id: Optional[UUID] = None
