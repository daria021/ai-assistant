from typing import Optional

from .abstract import UpdateDTO, CreateDTO


class CreateServiceDTO(CreateDTO):
    name: str
    is_active: bool


class UpdateServiceDTO(UpdateDTO):
    name: Optional[str] = None
    is_active: Optional[bool] = None
