from uuid import UUID

from fastapi import APIRouter
from shared.domain.dto.story_to_publish import CreateStoryToPublishDTO, UpdateStoryToPublishDTO

from dependencies.services.story_to_publish import get_story_to_publish_service

router = APIRouter(
    prefix="/story-to-publish",
    tags=["story-to-publish"],
)
#
#
# @router.post('')
# async def create_story_to_publish(story_to_publish: CreateStoryToPublishDTO) -> UUID:
#     story_to_publish_service = get_story_to_publish_service()
#     return await story_to_publish_service.create_story_to_publish(story_to_publish=story_to_publish)
#
#
# @router.get('/all')
# async def get_story_to_publishs():
#     story_to_publish_service = get_story_to_publish_service()
#     return await story_to_publish_service.get_all_stories_to_publish()
#
#
# @router.get('')
# async def get_story_to_publish(story_to_publish_id: UUID):
#     story_to_publish_service = get_story_to_publish_service()
#     return await story_to_publish_service.get_story_to_publish(story_to_publish_id=story_to_publish_id)
#
#
# @router.patch('')
# async def update_story_to_publish(story_to_publish: UpdateStoryToPublishDTO, story_to_publish_id: UUID):
#     story_to_publish_service = get_story_to_publish_service()
#     return await story_to_publish_service.update_story_to_publish(story_to_publish_id=story_to_publish_id,
#                                                                   story_to_publish=story_to_publish)
#
#
# @router.delete('/')
# async def delete_story_to_publish(story_to_publish_id: UUID):
#     story_to_publish_service = get_story_to_publish_service()
#     return await story_to_publish_service.delete_story_to_publish(story_to_publish_id=story_to_publish_id)
