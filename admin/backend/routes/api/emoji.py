from typing import List

from fastapi import APIRouter
from shared.dependencies.services.emoji import get_emoji_service
from shared.domain.models.emoji import Emoji

router = APIRouter(
    prefix="/emoji",
    tags=["emoji"]
)


@router.get("")
async def list_emojis() -> List[Emoji]:
    emoji_service = get_emoji_service()
    return await emoji_service.get_all_emojis()
