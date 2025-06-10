from abc import ABC

from abstractions.repositories import CRUDRepositoryInterface
from domain.dto.story import CreateStoryDTO, UpdateStoryDTO
from domain.models.story import Story


class StoryRepositoryInterface(
    CRUDRepositoryInterface[Story, CreateStoryDTO, UpdateStoryDTO],
    ABC,
):
    ...
