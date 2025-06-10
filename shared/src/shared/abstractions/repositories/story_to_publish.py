from abc import ABC

from shared.domain.dto import CreateStoryToPublishDTO, UpdateStoryToPublishDTO
from shared.domain.models import StoryToPublish
from .uuid_pk_abstract import UUIDPKRepositoryInterface


class StoryToPublishRepositoryInterface(
    UUIDPKRepositoryInterface[StoryToPublish, CreateStoryToPublishDTO, UpdateStoryToPublishDTO],
    ABC,
):
    ...
