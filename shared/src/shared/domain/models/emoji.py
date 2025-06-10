from typing import Optional

from .abstract import Model


class Emoji(Model):
    custom_emoji_id: str
    name: str
    img_url: str
