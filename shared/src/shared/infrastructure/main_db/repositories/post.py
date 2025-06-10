from dataclasses import dataclass
from uuid import UUID

from shared.abstractions.repositories import PostRepositoryInterface
from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.models import Post as PostModel
from shared.infrastructure.main_db.entities import Post
from .abstract import AbstractMainDBRepository


@dataclass
class PostRepository(
    AbstractMainDBRepository[Post, PostModel, CreatePostDTO, UpdatePostDTO],
    PostRepositoryInterface,
):
    async def update(self, obj_id: UUID, obj: UpdatePostDTO) -> PostModel:
        async with self.session_maker() as session:
            async with session.begin():
                entity = await session.get(self.entity, obj_id, options=self.options)
                for key, value in obj.model_dump(exclude_unset=True).items():
                    if key == 'entities' and value is not None:
                        value = [x.model_dump(mode='json') for x in value]

                    setattr(entity, key, value)

            await session.refresh(entity)

        return self.entity_to_model(entity)

    def create_dto_to_entity(self, dto: CreatePostDTO) -> Post:
        return Post(
            id=dto.id,
            text=dto.text,
            name=dto.name,
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
            image_path=entity.image_path,
            html=entity.html,
            entities=[MessageEntityDTO.model_validate(x) for x in entity.entities] if entity.entities else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
