from abc import ABC

from shared.domain.dto.update_post import UpdateUpdatePostDTO, CreateUpdatePostDTO
from shared.domain.models.update_post import UpdatePost
from .uuid_pk_abstract import UUIDPKRepositoryInterface


class UpdatePostRepositoryInterface(
    UUIDPKRepositoryInterface[UpdatePost, CreateUpdatePostDTO, UpdateUpdatePostDTO],
    ABC,
):
    ...