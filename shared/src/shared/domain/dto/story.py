from typing import Optional

from .abstract import CreateDTO, UpdateDTO


class CreateStoryDTO(CreateDTO):
    name: str
    file_path: str
    text: Optional[str] = None


class UpdateStoryDTO(UpdateDTO):
    name: Optional[str] = None
    file_path: Optional[str] = None
    text: Optional[str] = None
