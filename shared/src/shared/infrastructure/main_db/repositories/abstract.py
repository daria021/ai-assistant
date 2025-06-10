from abc import ABC
from uuid import UUID
from sqlalchemy import select
from shared.infrastructure.sqlalchemy.repository import AbstractSQLAlchemyRepository


class AbstractMainDBRepository[Entity, Model, CreateDTO, UpdateDTO](
    AbstractSQLAlchemyRepository[Entity, Model, CreateDTO, UpdateDTO, UUID],
    ABC,
):
    async def create(self, obj: CreateDTO) -> UUID:
        return UUID(str(await super().create(obj)))

    async def get_all(self, limit: int = 100, offset: int = 0, joined: bool = True) -> list[Model]:
        async with self.session_maker() as session:
            if joined:
                if self.options:
                    return [
                        self.entity_to_model(entity)
                        for entity in (await session.execute(
                            select(self.entity)
                            .order_by(self.entity.created_at.desc())
                            .limit(limit)
                            .offset(offset)
                            .options(*self.options)
                        )).unique().scalars().all()
                    ]
            res = (await session.execute(
                select(self.entity)
                .limit(limit)
                .offset(offset)
            )).scalars().all()
            return [
                self.entity_to_model(entity)
                for entity in res
            ]
