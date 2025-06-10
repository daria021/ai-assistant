import asyncio
import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.infrastructure.main_db import apply_migrations, MainDBSettings
from shared.settings import AbstractSettings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class MigratorSettings(AbstractSettings):
    main_db: MainDBSettings = Field(default_factory=MainDBSettings)

    model_config = SettingsConfigDict(
        extra="ignore",
        json_file=Path(__file__).parent / "settings.json",
        json_file_encoding="utf-8",
    )


async def main():
    settings = MigratorSettings()

    await apply_migrations(url=settings.main_db.url)
    logger.info("DB upgrade successfully")


if __name__ == '__main__':
    asyncio.run(main())
