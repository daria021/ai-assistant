import logging
import os
from dataclasses import field, dataclass
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import aiofiles

from shared.abstractions.services import UploadServiceInterface

logger = logging.getLogger(__name__)


@dataclass
class UploadService(UploadServiceInterface):
    public_backend_base_url: str
    images_dir: str = field(default="/app/upload")

    files_endpoint: str = 'upload'

    @staticmethod
    def get_extension(filename: str) -> str:
        return filename.split('.')[-1]

    def get_file_url(self, name: str) -> str:
        logger.info(f"getting file url for {name} ({self.files_endpoint} {self.public_backend_base_url})")
        return f'{self.public_backend_base_url}/{self.files_endpoint}/{name}'

    async def upload(self, file: bytes, extension: str) -> str:
        new_filename, new_filepath = self._get_new_file_path(extension)
        try:
            async with aiofiles.open(new_filepath, "wb") as f:
                await f.write(file)

            return new_filename
        except Exception:
            logger.error("There was an error while uploading file", exc_info=True)
            raise

    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.images_dir, filename)

    def _get_new_file_path(
            self,
            extension: str,
    ) -> tuple[
        Annotated[str, 'filename'],
        Annotated[str, 'file path'],
    ]:
        new_filename = f"{uuid4()}.{extension}"
        return new_filename, self.get_file_path(new_filename)

    async def initialize(self) -> None:
        images = Path(self.images_dir)

        if not images.exists():
            images.mkdir(parents=True, exist_ok=True)
