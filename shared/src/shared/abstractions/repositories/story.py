from abc import ABC

from shared.domain.dto.story import CreateStoryDTO, UpdateStoryDTO
from shared.domain.models import Story
from .uuid_pk_abstract import UUIDPKRepositoryInterface


class StoryRepositoryInterface(
    UUIDPKRepositoryInterface[Story, CreateStoryDTO, UpdateStoryDTO],
    ABC,
):
    ...
