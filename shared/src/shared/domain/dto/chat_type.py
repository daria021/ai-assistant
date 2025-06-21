from typing import Optional

from .abstract import CreateDTO, UpdateDTO


class CreateChatTypeDTO(CreateDTO):
    name: str
    description: str


class UpdateChatTypeDTO(UpdateDTO):
    name: Optional[str] = None
    description: Optional[str] = None
