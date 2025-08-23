import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Type, Optional
from asyncpg.pgproto.pgproto import UUID as asyncpgUUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload, InstrumentedAttribute

from shared.abstractions.repositories.abstract import CRUDRepositoryInterface
from shared.infrastructure.sqlalchemy.exceptions import NotFoundException
from sqlalchemy.inspection import inspect as sa_inspect

logger = logging.getLogger(__name__)


@dataclass
class AbstractSQLAlchemyRepository[Entity, Model, CreateDTO, UpdateDTO, PK_TYPE](
    CRUDRepositoryInterface[PK_TYPE, Model, CreateDTO, UpdateDTO],
):
    session_maker: async_sessionmaker

    joined_fields: dict[str, Optional[list[str]]] = field(default_factory=dict)
    options: list = field(default_factory=list)

    _soft_delete: bool = field(default=False)

    def __post_init__(self):
        self.entity: Type[Entity] = self.__orig_bases__[0].__args__[0]  # noqa
        self._set_lazy_fields()

    def _set_lazy_fields(self):
        if not self.joined_fields:
            return

        def convert_to_nested_dict(fields):
            return {field: {} for field in (fields or [])}

        def get_associated_entity_class(attr_field):
            """
            Extract the associated entity class from an InstrumentedAttribute.
            """
            if hasattr(attr_field, "comparator") and hasattr(attr_field.comparator, "prop"):
                relationship_prop = attr_field.comparator.prop
                if hasattr(relationship_prop, "mapper"):
                    return relationship_prop.mapper.entity
            return None

        def build_joinedload(attr_field, subfields, depth=0):
            """
            Recursively build joinedload options for nested relationships.
            """
            associated_entity = get_associated_entity_class(attr_field)
            if not associated_entity:
                raise ValueError(f"Cannot determine associated entity class for attribute {attr_field}")

            loader = joinedload(attr_field)
            for subfield, nested_subfields in subfields.items():
                nested_attr_field = getattr(associated_entity, subfield, None)
                if nested_attr_field is None:
                    raise ValueError(f"{subfield} is not a valid attribute of {associated_entity}")

                subloader = build_joinedload(nested_attr_field, nested_subfields, depth + 1)
                loader = loader.options(subloader)
            return loader

        # Convert self.joined_fields to nested dictionaries if not already
        joined_fields = {}
        for field in self.joined_fields:
            joined_fields[field] = convert_to_nested_dict(self.joined_fields[field])

        options_to_add = []
        for attr, subfields in joined_fields.items():
            attr_field: InstrumentedAttribute = getattr(self.entity, attr)
            if attr_field.comparator.prop.uselist:
                loader = build_joinedload(attr_field, subfields or {})
                options_to_add.append(loader)
            else:
                options_to_add.append(joinedload(attr_field))

        self.options.extend(options_to_add)

    async def create(self, obj: CreateDTO) -> int | asyncpgUUID:
        async with self.session_maker() as session:
            async with session.begin():
                entity = self.create_dto_to_entity(obj)
                session.add(entity)

            await session.refresh(entity)
            entity_id = entity.id

        return entity_id

    async def get(self, obj_id: PK_TYPE) -> Model:
        async with self.session_maker() as session:
            try:
                stmt = (
                    select(self.entity)
                    .where(self.entity.id == obj_id)
                )
                if self._soft_delete:
                    stmt = stmt.where(self.entity.deleted_at.is_(None))
                if self.options:
                    stmt = stmt.options(*self.options)

                res = await session.execute(stmt)

                if self.options:
                    res = res.unique()

                obj = res.scalars().one()
                return self.entity_to_model(obj) if obj else None
            except NoResultFound:
                raise NotFoundException

    async def update(self, obj_id: PK_TYPE, obj: UpdateDTO) -> Model:
        async with self.session_maker() as session:
            async with session.begin():
                entity = await session.get(self.entity, obj_id)
                if self._soft_delete and entity.deleted_at:
                    raise NotFoundException()

                for key, value in obj.model_dump(exclude_unset=True).items():
                    setattr(entity, key, value)

            await self._refresh_all(session, entity)

        return self.entity_to_model(entity)

    async def delete(self, obj_id: PK_TYPE) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                obj = await session.get(self.entity, obj_id)
                if not obj:
                    raise NotFoundException

                if self._soft_delete:
                    if obj.deleted_at:
                        raise NotFoundException
                    else:
                        obj.deleted_at = datetime.now()
                else:
                    await session.delete(obj)

    async def get_all(self, limit: int = 100, offset: int = 0, joined: bool = True) -> list[Model]:
        async with self.session_maker() as session:
            stmt = (
                select(self.entity)
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

    @abstractmethod
    def entity_to_model(self, entity: Entity) -> Model:
        ...

    @abstractmethod
    def create_dto_to_entity(self, dto: CreateDTO) -> Entity:
        ...

    # добавь в класс AbstractSQLAlchemyRepository
    @staticmethod
    async def _refresh_all(session, entity) -> None:
        mapper = sa_inspect(entity.__class__)
        column_names = [c.key for c in mapper.columns]
        relationship_names = [r.key for r in mapper.relationships]
        await session.refresh(entity, attribute_names=column_names + relationship_names)
