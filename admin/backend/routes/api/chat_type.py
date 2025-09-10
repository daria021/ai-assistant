import logging
from uuid import UUID

from fastapi import APIRouter
from shared.domain.dto.chat_type import CreateChatTypeDTO, UpdateChatTypeDTO
from shared.domain.models.chat_type import ChatType

from dependencies.services.chat_type import get_chat_type_service

router = APIRouter(
    prefix="/chat_type",
    tags=["chat_type"],
)

logger = logging.getLogger(__name__)


@router.get('')
async def get_chats_types() -> list[ChatType]:
    chat_type_service = get_chat_type_service()
    return await chat_type_service.get_chats_types()


@router.post("")
async def create_chat_type(request: CreateChatTypeDTO) -> None:
    chat_type_service = get_chat_type_service()
    await chat_type_service.create_chat_type(chat_type=request)


@router.get("/{chat_id}")
async def get_chat_type(chat_type_id: UUID) -> ChatType:
    chat_type_service = get_chat_type_service()
    return await chat_type_service.get_chat_type(chat_type_id=chat_type_id)


@router.delete("/{chat_type_id}")
async def delete_chat_type(chat_type_id: UUID) -> None:
    chat_type_service = get_chat_type_service()
    return await chat_type_service.delete_chat_type(chat_type_id=chat_type_id)


@router.patch("/{chat_type_id}")
async def update_chat_type(chat_type_id: UUID, request: UpdateChatTypeDTO) -> ChatType:
    chat_type_service = get_chat_type_service()
    return await chat_type_service.update_chat_type(chat_type_id=chat_type_id, chat_type=request)

