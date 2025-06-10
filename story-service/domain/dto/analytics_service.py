from typing import Optional

from domain.dto.base import CreateDTO, UpdateDTO


class CreateServiceDTO(CreateDTO):
    name: str
    is_active: bool

class UpdateServiceDTO(UpdateDTO):
    name: Optional[str] = None
    is_active: Optional[bool] = None