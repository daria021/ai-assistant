from uuid import UUID

from fastapi import APIRouter, Request
from shared.domain.dto.post_to_publish import CreatePostToPublishDTO, UpdatePostToPublishDTO

from dependencies.services.post_to_publish import get_post_to_publish_service

from shared.domain.models import PostToPublish

from routes.utils import get_user_id_from_request

router = APIRouter(
    prefix="/post-to-publish",
    tags=["post-to-publish"],
)


@router.post('')
async def create_post_to_publish(request: Request, post_to_publish: CreatePostToPublishDTO) -> UUID:
    post_to_publish_service = get_post_to_publish_service()
    user_id = get_user_id_from_request(request)
    post_to_publish.creator_id = user_id
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
