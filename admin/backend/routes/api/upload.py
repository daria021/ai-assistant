import logging

from fastapi import APIRouter
from starlette.responses import FileResponse

from dependencies.services.upload import get_upload_service

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

logger = logging.getLogger(__name__)


@router.get('/{filename}')
async def get_file(
        filename: str,
) -> FileResponse:
    upload_service = get_upload_service()

    file_path = upload_service.get_file_path(filename)

    return FileResponse(file_path)
