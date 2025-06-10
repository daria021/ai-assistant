from typing import Optional

from .abstract import Model


class Chat(Model):
    name: str
    chat_id: int
    invite_link: Optional[str] = None
