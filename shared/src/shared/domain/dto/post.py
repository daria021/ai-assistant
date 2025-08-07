from typing import Optional, List

from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .abstract import CreateDTO, UpdateDTO
from .post_to_publish import MessageEntityDTO


class CreatePostDTO(CreateDTO):
    name: str
    text: str
    image_path: Optional[str] = None
    is_template: bool
    html: Optional[str] = None
    entities: Optional[list[MessageEntityDTO]] = None

    @field_validator("entities", mode="after")
    def check_bounds(cls, entities: List[MessageEntityDTO], info: FieldValidationInfo) -> List[MessageEntityDTO]:
        txt = info.data.get("text", "")
        custom_emojis = 0
        for e in entities:
            if e.type == 'custom_emoji':
                custom_emojis += 1

            text_len = len(txt) + custom_emojis + len(txt.count('\n'))
            if not (0 <= e.offset < text_len and e.offset + e.length <= text_len):
                raise ValueError(
                    f"Entity out of bounds: offset={e.offset} length={e.length} for text of length {len(txt)}")

        return entities


class UpdatePostDTO(UpdateDTO):
    name: Optional[str] = None
    text: Optional[str] = None
    image_path: Optional[str] = None
    is_template: Optional[bool] = None
    html: Optional[str] = None
    entities: Optional[list[MessageEntityDTO]] = None

    @field_validator("entities", mode="after")
    def check_bounds(cls, entities: List[MessageEntityDTO], info: FieldValidationInfo) -> List[MessageEntityDTO]:
        txt = info.data.get("text", "")
        if not txt:
            return entities

        custom_emojis = 0
        for e in entities:
            if e.type == 'custom_emoji':
                custom_emojis += 1

            text_len = len(txt) + custom_emojis
            if not (0 <= e.offset < text_len and e.offset + e.length <= text_len):
                raise ValueError(
                    f"Entity out of bounds: offset={e.offset} length={e.length} for text of length {len(txt)}")

        return entities
