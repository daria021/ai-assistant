from typing import Optional

from .abstract import CreateDTO, UpdateDTO


class CreateProxyDTO(CreateDTO):
    proxy_string: str
    is_free: bool = True
    is_deprecated: bool = False


class UpdateProxyDTO(UpdateDTO):
    proxy_string: Optional[str] = None
    is_free: Optional[bool] = None
    is_deprecated: Optional[bool] = None
