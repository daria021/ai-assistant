from abc import ABC, abstractmethod

from shared.domain.dto import CreateProxyDTO, UpdateProxyDTO
from shared.domain.models import Proxy
from .uuid_pk_abstract import UUIDPKRepositoryInterface


class ProxyRepositoryInterface(
    UUIDPKRepositoryInterface[Proxy, CreateProxyDTO, UpdateProxyDTO],
    ABC,
):
    @abstractmethod
    async def get_available_proxies_count(self) -> int:
        ...

    @abstractmethod
    async def get_available_proxy(self) -> Proxy:
        ...
