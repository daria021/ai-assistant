import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from shared.abstractions.services import UploadServiceInterface
from shared.domain.dto.story import CreateStoryDTO, UpdateStoryDTO

from dependencies.services.story import get_story_service
from dependencies.services.upload import get_upload_service

router = APIRouter(
    prefix="/story",
    tags=["story"],
)

logger = logging.getLogger(__name__)


@router.post('')
async def create_story(
        name: str = Form(...),
        text: str = Form(...),
        image: Optional[UploadFile] = File(None),
        upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> UUID:
    story_service = get_story_service()
    image_path = None
    if image is not None:
        try:
            extension = upload_service.get_extension(image.filename)
            image_path = await upload_service.upload(image.file.read(), extension)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Не удалось сохранить файл"
            ) from e
    else:
        logger.error("ATTENTION!!! IMAGE IS NONE")

    story = CreateStoryDTO(
        name=name,
        text=text,
        file_path=image_path,
    )
    return await story_service.create_story(story=story)


@router.get('/all')
async def get_stories():
    story_service = get_story_service()
    return await story_service.get_all_stories()


@router.get('')
async def get_story(story_id: UUID):
    story_service = get_story_service()
    return await story_service.get_story(story_id=story_id)


@router.patch('')
async def update_story(story: UpdateStoryDTO, story_id: UUID):
    story_service = get_story_service()
    return await story_service.update_story(story_id=story_id, story=story)


@router.delete('/')
async def delete_story(story_id: UUID):
    story_service = get_story_service()
    return await story_service.delete_story(story_id=story_id)
