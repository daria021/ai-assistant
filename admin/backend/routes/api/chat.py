import logging

from fastapi import APIRouter, HTTPException, status
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


@router.post("")
async def create_chat(request: CreateChatRequest) -> Chat:
    """
    Создаёт новую запись чата по invite_link.
    """
    chat_service = get_chat_service()
    try:
        new_chat_id = await chat_service.create_chat_by_link(request.invite_link)
        return new_chat_id
    except ChatAlreadyExistsError:
        # если чат с таким invite_link уже есть
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
