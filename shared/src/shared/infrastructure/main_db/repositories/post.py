import logging
from dataclasses import dataclass, field
from uuid import UUID

from shared.abstractions.repositories import PostRepositoryInterface
from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.models import Post as PostModel
from shared.infrastructure.main_db.entities import Post
from .abstract import AbstractMainDBRepository
from sqlalchemy import select
logger = logging.getLogger(__name__)

@dataclass
class PostRepository(
    AbstractMainDBRepository[Post, PostModel, CreatePostDTO, UpdatePostDTO],
    PostRepositoryInterface,
):

    _soft_delete: bool = field(default=True)

    async def update(self, obj_id: UUID, obj: UpdatePostDTO) -> PostModel:
        async with self.session_maker() as session:
            async with session.begin():
                entity = await session.get(self.entity, obj_id, options=self.options)
                if entity.deleted_at is None:
                    for key, value in obj.model_dump(exclude_unset=True, exclude={'entiites'}).items():
                        setattr(entity, key, value)

                    if obj.entities:
                        entity.entities = [x.model_dump(mode='json') for x in obj.entities]

            await session.refresh(entity)

        return self.entity_to_model(entity)

    async def get_all(self, limit: int = 100, offset: int = 0, joined: bool = True) -> list[Post]:
        async with self.session_maker() as session:
            stmt = (
                select(self.entity)
                .where(self.entity.deleted_at.is_(None))
                .limit(limit)
                .offset(offset)
            )
            if joined and self.options:
                stmt = stmt.options(*self.options)

            if self._soft_delete:
                stmt = stmt.where(self.entity.deleted_at.is_(None))

            res = await session.execute(stmt)

            if self.options:
                res = res.unique()

            objs = res.scalars().all()

            return [self.entity_to_model(entity) for entity in objs]


    def create_dto_to_entity(self, dto: CreatePostDTO) -> Post:
        return Post(
            id=dto.id,
            text=dto.text,
            name=dto.name,
            is_template=dto.is_template,
            image_path=dto.image_path,
            html=dto.html,
            entities=[x.model_dump(mode='json') for x in dto.entities] if dto.entities else None,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: Post) -> Post:
        return PostModel(
            id=entity.id,
            text=entity.text,
            name=entity.name,
            is_template=entity.is_template,
            image_path=entity.image_path,
            html=entity.html,
            entities=[MessageEntityDTO.model_validate(x) for x in entity.entities] if entity.entities else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
