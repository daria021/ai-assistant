import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from shared.infrastructure.main_db import init_db

from routes import (
    watch_router,
)
from settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(_) -> AsyncGenerator[None, None]:
    init_db(settings.db.url)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(watch_router)
