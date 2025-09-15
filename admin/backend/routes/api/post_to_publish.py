import logging
from uuid import UUID

from fastapi import APIRouter, Request
from shared.domain.dto.post_to_publish import CreatePostToPublishDTO, UpdatePostToPublishDTO

from dependencies.services.post import get_post_service
from dependencies.services.post_to_publish import get_post_to_publish_service

from shared.domain.models import PostToPublish

from routes.utils import get_user_id_from_request
from shared.dependencies.repositories.post import get_post_repository
from shared.domain.dto import CreatePostDTO

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/post-to-publish",
    tags=["post-to-publish"],
)


@router.post('')
async def create_post_to_publish(request: Request, post_to_publish: CreatePostToPublishDTO) -> UUID:
    """
    Создаёт запись для публикации, предварительно клонируя текущий пост.
    Это фиксирует контент на момент нажатия кнопки, чтобы последующие правки
    исходного шаблона не затрагивали уже запланированные отправки.
    """
    user_id = get_user_id_from_request(request)

    logger.info(f"Creating post to publish, user_id={user_id}, dto={post_to_publish}")

    # 1) Получаем исходный пост без преобразования image_path в URL
    post_repository = get_post_repository()
    original_post = await post_repository.get(post_to_publish.post_id)
    logger.info(f"Original post: {original_post}")

    # 2) Клонируем пост (image_path оставляем как есть — путь в сторе)
    post_service = get_post_service()
    clone_dto = CreatePostDTO(
        name=original_post.name,
        text=original_post.text,
        is_template=False,              # клон — не шаблон
        image_path=original_post.image_path,
        html=original_post.html,
        entities=original_post.entities,
    )
    logger.info(f"Cloning post DTO: {clone_dto}")
    cloned_post_id = await post_service.create_post(post=clone_dto, author_id=user_id)
    logger.info(f"Cloned post ID: {cloned_post_id}")

    # 3) Подменяем post_id на клон и сохраняем запись публикации
    post_to_publish.creator_id = user_id
    post_to_publish.post_id = cloned_post_id

    logger.info(f"Creating PostToPublish with DTO: {post_to_publish}")

    post_to_publish_service = get_post_to_publish_service()
    return await post_to_publish_service.create_post_to_publish(post_to_publish=post_to_publish)


@router.get('/all')
async def get_posts_to_publish(request: Request) -> list[PostToPublish]:
    user_id = get_user_id_from_request(request)
    post_to_publish_service = get_post_to_publish_service()
    return await post_to_publish_service.get_posts_to_publish(user_id)


@router.get('')
async def get_post_to_publish(
        post_to_publish_id: UUID,
) -> PostToPublish:
    post_to_publish_service = get_post_to_publish_service()
    return await post_to_publish_service.get_post_to_publish(post_to_publish_id=post_to_publish_id)


@router.patch('/{post_to_publish_id}')
async def update_post_to_publish(post_to_publish: UpdatePostToPublishDTO, post_to_publish_id: UUID):
    post_to_publish_service = get_post_to_publish_service()
    return await post_to_publish_service.update_post_to_publish(post_to_publish_id=post_to_publish_id,
                                                                post_to_publish=post_to_publish)

@router.delete('')
async def delete_post_to_publish(post_to_publish_id: UUID):
    post_to_publish_service = get_post_to_publish_service()
    return await post_to_publish_service.delete_post_to_publish(post_to_publish_id=post_to_publish_id)
