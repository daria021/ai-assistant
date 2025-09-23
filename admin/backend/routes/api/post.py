import json
import logging
from typing import Optional, Annotated
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, Request, Response
from shared.abstractions.services import UploadServiceInterface
from shared.domain.dto import UpdatePostDTO, CreatePostDTO
from shared.domain.dto.post_to_publish import MessageEntityDTO
from shared.domain.models import Post

from dependencies.services.post import get_post_service
from dependencies.services.upload import get_upload_service
from forms.update_post_form import UpdatePostForm
from routes.utils import get_user_id_from_request

router = APIRouter(
    prefix="/post",
    tags=["post"],
)

logger = logging.getLogger(__name__)


@router.post('')
async def create_post(
        request: Request,
        name: str = Form(...),
        text: str = Form(...),
        html: str = Form(...),
        is_template: bool = Form(...),
        entities: str = Form(...),
        image: Optional[UploadFile] = File(None),
        # allow cloning existing image by passing its stored filename
        image_path: Optional[str] = Form(None),
        upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> UUID:
    author_id = get_user_id_from_request(request)
    post_service = get_post_service()
    image_filename: Optional[str] = None
    if image is not None:
        try:
            extension = upload_service.get_extension(image.filename)
            image_filename = await upload_service.upload(image.file.read(), extension)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Не удалось сохранить файл"
            ) from e
    elif image_path:
        # clone existing stored filename (no upload). Accept raw filename or full URL.
        try:
            # avoid importing os.path just for basename; simple split works
            image_filename = image_path.split('/')[-1]
        except Exception:
            image_filename = image_path

    dsrslzd_entities = json.loads(entities)
    entities = [MessageEntityDTO.model_validate(e) for e in dsrslzd_entities]

    post = CreatePostDTO(
        name=name,
        text=text,
        is_template=is_template,
        image_path=image_filename,
        html=html,
        entities=entities,
    )
    return await post_service.create_post(post=post, author_id=author_id)


@router.get('/all')
async def get_post():
    post_service = get_post_service()
    return await post_service.get_all_posts()


@router.get('/templates')
async def get_templates():
    post_service = get_post_service()
    return await post_service.get_templates()


@router.get('')
async def get_post(post_id: UUID):
    post_service = get_post_service()
    return await post_service.get_post(post_id=post_id)


@router.patch('/{post_id}')
async def update_post(
        request: Request,
        post_id: UUID,
        data: Annotated[UpdatePostForm, Form()],
        upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> Post:
    author_id = get_user_id_from_request(request)
    post_service = get_post_service()

    data_dump = data.model_dump(exclude_unset=True)

    if data.image:
        extension = upload_service.get_extension(data.image.filename)
        image_path = await upload_service.upload(data.image.file.read(), extension)
        data_dump["image_path"] = image_path

    if data.entities:
        entities = [MessageEntityDTO.model_validate(e) for e in json.loads(data.entities)]
        data_dump["entities"] = entities

    post_dto = UpdatePostDTO.model_validate(data_dump)

    return await post_service.update_post(post_id=post_id, post=post_dto, author_id=author_id)


@router.delete('/')
async def delete_post(post_id: UUID):
    post_service = get_post_service()
    return await post_service.delete_post(post_id=post_id)
