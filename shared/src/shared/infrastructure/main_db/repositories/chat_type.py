from dataclasses import dataclass, field
from typing import Optional, List

from shared.abstractions.repositories.chat_type import ChatTypeRepositoryInterface
from shared.domain.dto.chat_type import CreateChatTypeDTO, UpdateChatTypeDTO
from shared.domain.models.chat_type import ChatType as ChatTypeModel
from shared.infrastructure.main_db.entities import ChatType
from .abstract import AbstractMainDBRepository


@dataclass
class ChatTypeRepository(
    AbstractMainDBRepository[ChatType, ChatTypeModel, CreateChatTypeDTO, UpdateChatTypeDTO],
    ChatTypeRepositoryInterface,
):
    joined_fields: dict[str, Optional[List[str]]] = field(
        default_factory=lambda: {
            "chats": None,
        },
    )

    def create_dto_to_entity(self, dto: CreateChatTypeDTO) -> ChatType:
        return ChatType(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def entity_to_model(self, entity: ChatType) -> ChatTypeModel:
        return ChatTypeModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
