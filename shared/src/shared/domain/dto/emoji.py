from typing import Optional

from .abstract import CreateDTO, UpdateDTO
from ...infrastructure.main_db.entities import EmojiFormat


class CreateEmojiDTO(CreateDTO):
    name: str
    custom_emoji_id: str
    img_url: str
    format: EmojiFormat


class UpdateEmojiDTO(UpdateDTO):
    name: Optional[str] = None
    custom_emoji_id: Optional[str] = None
    img_url: Optional[str] = None
    format: EmojiFormat | None = None
