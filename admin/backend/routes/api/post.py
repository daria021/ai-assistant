import json
import logging
from typing import Optional, Annotated
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from shared.abstractions.services import UploadServiceInterface
from shared.domain.dto import UpdatePostDTO, CreatePostDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.models import Post

from dependencies.services.post import get_post_service
from dependencies.services.upload import get_upload_service
from forms.update_post_form import UpdatePostForm

router = APIRouter(
    prefix="/post",
    tags=["post"],
)

logger = logging.getLogger(__name__)


@router.post('')
async def create_post(
        name: str = Form(...),
        text: str = Form(...),
        html: str = Form(...),
        is_template: bool = Form(...),
        entities: str = Form(...),
        image: Optional[UploadFile] = File(None),
        upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> UUID:
    post_service = get_post_service()
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

    logger.info(entities)
    dsrslzd_entities = json.loads(entities)
    logger.debug("BACK_IN_POST text=%r ENT=%s\", text[:200], dsrslzd_entities[:8]")

    logger.info(dsrslzd_entities)
    entities = [MessageEntityDTO.model_validate(e) for e in dsrslzd_entities]

    post = CreatePostDTO(
        name=name,
        text=text,
        is_template=is_template,
        image_path=image_path,
        html=html,
        entities=entities,
    )
    logger.debug('BACK_IN_POST', repr(post.text)[:200], post.entities[:8])
    return await post_service.create_post(post=post)


@router.get('/all')
async def get_post():
    post_service = get_post_service()
    return await post_service.get_all_posts()


@router.get('')
async def get_post(post_id: UUID):
    post_service = get_post_service()
    return await post_service.get_post(post_id=post_id)


@router.patch('/{post_id}')
async def update_post(
        post_id: UUID,
        data: Annotated[UpdatePostForm, Form()],
        upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> Post:
    post_service = get_post_service()

    data_dump = data.model_dump(exclude_unset=True)

    if data.image:
        extension = upload_service.get_extension(data.image.filename)
        image_path = await upload_service.upload(data.image.file.read(), extension)
        data_dump["image_path"] = image_path

    if data.entities:
        entities = [MessageEntityDTO.model_validate(e) for e in json.loads(data.entities)]
        data_dump["entities"] = entities

    logger.info(data.entities)
    # logger.info(data_dump["entities"])

    post_dto = UpdatePostDTO.model_validate(data_dump)

    logger.info(post_dto.entities)

    return await post_service.update_post(post_id=post_id, post=post_dto)


@router.delete('/')
async def delete_post(post_id: UUID):
    post_service = get_post_service()
    return await post_service.delete_post(post_id=post_id)
