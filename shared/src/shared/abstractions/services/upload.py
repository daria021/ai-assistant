from abc import ABC, abstractmethod


class UploadServiceInterface(ABC):
    @abstractmethod
    async def upload(self, file: bytes, extension: str) -> str:
        ...

    @abstractmethod
    def get_file_path(self, filename: str) -> str:
        ...

    @abstractmethod
    async def initialize(self) -> None:
        ...

    @abstractmethod
    def get_file_url(self, name: str) -> str:
        ...

    @staticmethod
    @abstractmethod
    def get_extension(filename: str) -> str:
        ...
