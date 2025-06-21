from typing import Optional

from .abstract import Model


class ChatType(Model):
    name: str
    description: str
    chats: Optional[list[str]] = None
