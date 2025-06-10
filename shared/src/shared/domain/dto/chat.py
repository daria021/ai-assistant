from typing import Optional

from .abstract import CreateDTO, UpdateDTO


class CreateChatDTO(CreateDTO):
    name: str
    chat_id: int
    invite_link: Optional[str] = None


class UpdateChatDTO(UpdateDTO):
    name: Optional[str] = None
    chat_id: Optional[int] = None
    invite_link: Optional[str] = None
