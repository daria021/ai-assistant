import asyncio
import logging

from shared.infrastructure.main_db import init_db

from dependencies.services.consumer import get_posts_consumer
from settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def main():
    logger.info("Starting posting service")

    init_db(settings.db.url)

    consumer = get_posts_consumer()

    try:
        await consumer.execute()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
        exit(0)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        exit(1)


logger.info(__name__)

if __name__ == "__main__":

    asyncio.run(main())

