from typing import Optional
from uuid import UUID

from .abstract import CreateDTO, UpdateDTO


class CreateUpdatePostDTO(CreateDTO):
    post_id: UUID
    post_json: dict
    author_id: UUID


class UpdateUpdatePostDTO(UpdateDTO):
    post_id: Optional[UUID] = None
    post_json: Optional[dict] = None
    author_id: Optional[UUID] = None
