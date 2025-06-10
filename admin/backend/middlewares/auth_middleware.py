import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from shared.infrastructure.sqlalchemy import NotFoundException

from dependencies.services.auth import get_auth_service
from services.auth.exceptions import InvalidTokenException, ExpiredTokenException
from services.exceptions import PermissionException, BannedUserException


async def check_for_auth(
        request: Request,
        call_next,
):
    url_path = request.url.path.replace("/api", "")
    if (
            url_path.startswith("/auth") or
            url_path.startswith("/docs") or
            url_path.startswith("/openapi") or
            url_path.startswith("/upload") or
            request.method == 'OPTIONS'
    ):
        response = await call_next(request)
        return response

    if 'Authorization' not in request.headers:
        return JSONResponse(
            status_code=401,
            content={
                'detail': 'Token is empty',
            }
        )

    access_token = request.headers['Authorization'].replace('Bearer ', '')

    auth_service = get_auth_service()
    try:
        # user_id = UUID('')
        user_id = await auth_service.get_user_id_from_jwt(access_token)
    except Exception as e:
        logging.getLogger(__name__).error(f"fuuuck {access_token}", exc_info=True)
        code, detail = 401, 'Unknown authorization exception'
        match e:
            case InvalidTokenException():
                detail = 'Token is invalid'
            case ExpiredTokenException():
                detail = 'Token is expired'
            case NotFoundException():
                detail = 'User ID found in token does not exist'
            case BannedUserException():
                detail = "You're banned"
                code = 403

        return JSONResponse(
            status_code=code,
            content={
                'detail': detail,
            }
        )

    request.scope['x_user_id'] = user_id
    try:
        response = await call_next(request)
        return response
    except PermissionException as e:
        return JSONResponse(
            status_code=403,
            content={
                'detail': "You're lacking permissions to do this.",
            }
        )
