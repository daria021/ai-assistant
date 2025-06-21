import logging
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException
from shared.domain.dto import CreateUserDTO, UpdateUserDTO
from shared.domain.models import User
from shared.infrastructure.main_db import NoFreeProxiesException

from dependencies.services.user import get_user_service
from routes.requests.user import VerifyAuthCodeRequest
from routes.utils import get_user_id_from_request
from services.exceptions import UserHasNoProxyException

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

logger = logging.getLogger(__name__)


@router.post('')
async def create_user(user: CreateUserDTO) -> UUID:
    user_service = get_user_service()
    return await user_service.create_user(user=user)


@router.get('/all')
async def get_users():
    user_service = get_user_service()
    return await user_service.get_all_users()

@router.get('/managers')
async def get_managers():
    user_service = get_user_service()
    return await user_service.get_managers()


@router.get('')
async def get_user(user_id: UUID):
    user_service = get_user_service()
    return await user_service.get_user(user_id=user_id)


@router.patch('/{user_id}')
async def update_user(user: UpdateUserDTO, user_id: UUID) -> User:
    user_service = get_user_service()
    return await user_service.update_user(user_id=user_id, user=user)


@router.delete('')
async def delete_user(user_id: UUID):
    user_service = get_user_service()
    return await user_service.delete_user(user_id=user_id)


@router.get('/me')
async def get_me(
        request: Request,
) -> User:
    user_service = get_user_service()
    user_id = get_user_id_from_request(request)
    return await user_service.get_user(user_id=user_id)


@router.get("/code")
async def send_auth_code(
        phone: str,
        request: Request,
) -> None:
    user_service = get_user_service()
    user_id = get_user_id_from_request(request)

    try:
        await user_service.send_auth_code(phone=phone, user_id=user_id)
    except NoFreeProxiesException:
        raise HTTPException(
            status_code=503,
            detail="No free proxies found",
        )


@router.post("/code")
async def check_auth_code(
        request: Request,
        verify_request: VerifyAuthCodeRequest,
) -> None:
    user_service = get_user_service()
    user_id = get_user_id_from_request(request)
    try:
        await user_service.get_session_string_for_user(
            phone=verify_request.phone,
            code=verify_request.code,
            password=verify_request.password,
            user_id=user_id,
        )
    except UserHasNoProxyException:
        raise HTTPException(
            status_code=409,
            detail='User has no connected proxy',
        )
