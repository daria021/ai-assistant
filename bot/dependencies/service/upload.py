from shared.abstractions.services import UploadServiceInterface
from shared.dependencies.services import get_upload_service as get_base_upload_service

from settings import settings


def get_upload_service() -> UploadServiceInterface:
    return get_base_upload_service(
        public_backend_base_url=settings.env.api_host,
    )
