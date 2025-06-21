from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    invite_link: str
    manager_id: UUID
    chat_type_id: Optional[UUID] = None
