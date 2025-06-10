from typing import Optional

from shared.abstractions.services import UploadServiceInterface
from shared.services import UploadService


def get_upload_service(public_backend_base_url: str, app_upload_dir: Optional[str] = None) -> UploadServiceInterface:
    if app_upload_dir is None:
        return UploadService(
            public_backend_base_url=public_backend_base_url,
        )

    return UploadService(
        images_dir=app_upload_dir,
        public_backend_base_url=public_backend_base_url,
    )
