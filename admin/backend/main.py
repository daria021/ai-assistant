import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.openapi.utils import get_openapi
from shared.infrastructure.main_db import init_db
from settings import settings
from middlewares.auth_middleware import check_for_auth
# from middlewares import check_for_auth
from routes import (
    api_router,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG if settings.environment.is_debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(_) -> AsyncGenerator[None, None]:
    init_db(settings.db.url)

    yield


app = FastAPI(lifespan=lifespan)

app.middleware('http')(check_for_auth)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.jwt.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router)

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Assistant Admin Panel API",
#         version="0.1.0",
#         description="meow",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "bearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT",
#         }
#     }
#     openapi_schema["security"] = [{"bearerAuth": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema
#
#
# app.openapi = custom_openapi
