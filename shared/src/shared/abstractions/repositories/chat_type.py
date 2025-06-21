from abc import ABC

from shared.domain.dto.chat_type import CreateChatTypeDTO, UpdateChatTypeDTO
from shared.domain.models.chat_type import ChatType
from .uuid_pk_abstract import UUIDPKRepositoryInterface


class ChatTypeRepositoryInterface(
    UUIDPKRepositoryInterface[ChatType, CreateChatTypeDTO, UpdateChatTypeDTO],
    ABC,
):
    ...
