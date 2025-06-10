from abc import ABC

from .uuid_pk_abstract import UUIDPKRepositoryInterface
from ...domain.dto.emoji import CreateEmojiDTO, UpdateEmojiDTO
from ...domain.models.emoji import Emoji


class EmojisRepositoryInterface(
    UUIDPKRepositoryInterface[Emoji, CreateEmojiDTO, UpdateEmojiDTO],
    ABC,
):
    ...
