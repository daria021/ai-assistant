import logging
from dataclasses import dataclass, field

from shared.abstractions.repositories.update_post import UpdatePostRepositoryInterface
from shared.domain.dto.update_post import CreateUpdatePostDTO, UpdateUpdatePostDTO
from shared.domain.models.update_post import UpdatePost as UpdatePostModel
from shared.infrastructure.main_db.entities import UpdatePost
from .abstract import AbstractMainDBRepository

logger = logging.getLogger(__name__)

@dataclass
class UpdatePostRepository(
    AbstractMainDBRepository[UpdatePost, UpdatePostModel, CreateUpdatePostDTO, UpdateUpdatePostDTO],
    UpdatePostRepositoryInterface,
):

    _soft_delete: bool = field(default=True)

    def create_dto_to_entity(self, dto: CreateUpdatePostDTO) -> UpdatePost:
        return UpdatePost(
            id=dto.id,
            post_id=dto.post_id,
            post_json=dto.post_json,
            author_id=dto.author_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: UpdatePost) -> UpdatePost:
        return UpdatePostModel(
            id=entity.id,
            post_id=entity.post_id,
            post_json=entity.post_json,
            author_id=entity.author_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
