import asyncio
import logging

from shared.infrastructure.main_db import init_db

from dependencies.services.consumer import get_consumer
from dependencies.services.container_manager import get_container_manager
from settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def main():
    logger.info("Initializing service...")

    init_db(settings.db.url)
    consumer = get_consumer()

    container_manager = get_container_manager()

    logger.info("Service initialized, starting...")

    try:
        await asyncio.gather(consumer.execute(), container_manager.start_watching())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error("Unexpected exception", exc_info=True)
    finally:
        logger.info("Service has been successfully shut down")


if __name__ == '__main__':
    asyncio.run(main())
