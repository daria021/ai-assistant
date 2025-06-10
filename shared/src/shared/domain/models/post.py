from typing import Optional

from pydantic import ConfigDict
from sqlalchemy.orm import Mapped

from .abstract import Model
from shared.domain.dto.post_to_publish import MessageEntityDTO


class Post(Model):
    text: str
    name: str
    image_path: Optional[str] = None

    html: Optional[str] = None
    entities: Optional[list[MessageEntityDTO]] = None

    model_config = ConfigDict(from_attributes=True)

