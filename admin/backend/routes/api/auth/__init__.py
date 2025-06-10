from domain.schemas.auth import Credentials
from fastapi import APIRouter, Depends
from forms.auth_code_form import auth_code_form
from starlette.responses import JSONResponse

from abstractions.services.auth.service import AuthServiceInterface
from abstractions.services.exceptions import WrongCredentialsException
from dependencies.services.auth import get_auth_service
from routes.requests.auth import TelegramAuthRequest

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

# templates = Jinja2Templates(directory='templates')

@router.post("/telegram")
async def telegram_auth(payload: TelegramAuthRequest):
    auth_service = get_auth_service()

    tokens = await auth_service.create_token(init_data=payload.initData)

    return tokens


@router.post("")
async def validate_auth_code_backend(
        credentials: Credentials = Depends(auth_code_form),
        auth_service: AuthServiceInterface = Depends(get_auth_service),
) -> JSONResponse:
    try:
        tokens = await auth_service.create_token(credentials)
        response = JSONResponse(content={"status": "ok"}, status_code=200)
        response.set_cookie(key="access_token", value=tokens.access_token)
        # response.set_cookie(key="refresh_token", value=tokens.refresh_token)
        return response
    except WrongCredentialsException:
        return JSONResponse(content={"status": "error", "message": "Wrong credentials"}, status_code=400)
