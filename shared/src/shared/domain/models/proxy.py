from typing import Optional, TYPE_CHECKING

from .abstract import Model

if TYPE_CHECKING:
    from .user import User


class Proxy(Model):
    proxy_string: str
    is_free: bool
    is_deprecated: bool

    user: Optional['User'] = None
