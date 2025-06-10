from abc import ABC

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from shared.domain.dto import CreatePostDTO, UpdatePostDTO
from shared.domain.models import Post


class PostRepositoryInterface(
    UUIDPKRepositoryInterface[Post, CreatePostDTO, UpdatePostDTO],
    ABC,
):
    ...
