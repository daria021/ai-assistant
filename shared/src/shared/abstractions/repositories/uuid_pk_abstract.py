from abc import ABC
from uuid import UUID

from .abstract import CRUDRepositoryInterface


class UUIDPKRepositoryInterface[Model, CreateDTO, UpdateDTO](
    CRUDRepositoryInterface[UUID, Model, CreateDTO, UpdateDTO],
    ABC,
):
    ...
