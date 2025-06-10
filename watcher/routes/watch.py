import logging

from fastapi import APIRouter, HTTPException
from shared.domain.requests import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest

from dependencies.services.watcher import get_watcher
from services.exceptions import RepeatedRegistrationException

router = APIRouter(
    prefix='/watch',
)

logger = logging.getLogger(__name__)

@router.post('/message')
async def message(report: MessageSentRequest):
    watcher = get_watcher()
    try:
        await watcher.register_message(report)
    except RepeatedRegistrationException as e:
        logger.error(e)
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
