import logging
from dataclasses import dataclass

from sqlalchemy import select

from abstractions.repositories import UserRepositoryInterface
from infrastructure.repositories.sqlalchemy import AbstractSQLAlchemyRepository
from domain.dto.user import CreateUserDTO, UpdateUserDTO
from domain.models.user import User as UserModel

from infrastructure.entities import User

logger = logging.getLogger(__name__)


@dataclass
class UserRepository(
    AbstractSQLAlchemyRepository[User, UserModel, CreateUserDTO, UpdateUserDTO],
    UserRepositoryInterface,
):

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        async with self.session_maker() as session:
            user = await session.execute(
                select(self.entity)
                .where(self.entity.telegram_id == telegram_id)
                .options(*self.options)
            )
            user = user.unique().scalars().one_or_none()

        return self.entity_to_model(user) if user else None


    def create_dto_to_entity(self, dto: CreateUserDTO) -> User:
        return User(
            id=dto.id,
            nickname=dto.nickname,
            telegram_id=dto.telegram_id,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            nickname=entity.nickname,
            status=entity.status,
            telegram_id=entity.telegram_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
