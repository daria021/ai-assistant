from typing import Optional

from domain.dto.base import UpdateDTO, CreateDTO


class CreateServiceDTO(CreateDTO):
    name: str
    is_active: bool

class UpdateServiceDTO(UpdateDTO):
    name: Optional[str]
    is_active: Optional[bool]
