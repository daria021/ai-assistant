import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Response
from shared.domain.dto import UpdateChatDTO
from shared.domain.models import Chat
from shared.domain.requests.chat import CreateChatRequest

from dependencies.services.chat import get_chat_service
from services.exceptions import ChatAlreadyExistsError, InvalidInviteLinkError

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

logger = logging.getLogger(__name__)


@router.get('')
async def get_chats() -> list[Chat]:
    chat_service = get_chat_service()
    return await chat_service.get_chats()


@router.get('/type/{chat_type_id}')
async def get_chats_by_chat_type_id(chat_type_id: UUID) -> list[Chat]:
    chat_service = get_chat_service()
    return await chat_service.get_chats_by_type(type_id=chat_type_id)


@router.patch('/{chat_id}')
async def update_chat(chat_id: UUID, request: UpdateChatDTO) -> Chat:
    """
    Обновляет запись чата.
    """
    chat_service = get_chat_service()
    return await chat_service.update_chat(chat_id=chat_id, chat=request)

@router.delete('/{chat_id}')
async def delete_chat(chat_id: UUID) -> None:
    chat_service = get_chat_service()
    return await chat_service.delete_chat(chat_id=chat_id)

@router.post("")
async def create_chat(request: CreateChatRequest) -> Chat:
    """
    Создаёт новую запись чата по invite_link.
    """
    chat_service = get_chat_service()
    try:
        new_chat_id = await chat_service.create_chat_by_link(
            invite_link=request.invite_link,
            type_id=request.chat_type_id,
            manager_id=request.manager_id,
        )
        return new_chat_id
    except ChatAlreadyExistsError:
        # если чат с таким invite_link уже есть — попробуем вернуть id существующего
        chat_service = get_chat_service()
        try:
            # Собираем канонизированную ссылку ровно как в сервисе (strip)
            link = request.invite_link.strip()
            existing = await chat_service.chats_repository.get_by_invite_link(link)  # type: ignore[attr-defined]
            if existing:
                return Response(
                    status_code=status.HTTP_409_CONFLICT,
                    content=f'{{"id":"{existing.id}","chat_type_id":"{existing.chat_type_id}"}}',
                    media_type="application/json",
                )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chat with this invite_link already exists"
        )
    except InvalidInviteLinkError:
        # если ссылка неверная
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite link"
        )
    except Exception as e:
        # общий catch-all на всякий случай
        logger.exception("Error creating chat")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
