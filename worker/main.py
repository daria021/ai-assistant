import logging

from shared.infrastructure.main_db import init_db

from dependencies.services.message_consumer import get_message_consumer
from services.exceptions import NoMessagesShutdown
from user_bot.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    init_db(settings.db.url)

    consumer = get_message_consumer()

    try:
        await consumer.execute()
    except NoMessagesShutdown:
        logger.info("No messages in queue, shutting down...")
        exit(0)
    except KeyboardInterrupt:
        logger.info(f"Received KeyboardInterrupt, shutting down...")
        exit(0)
    except Exception as e:
        logger.error(e, exc_info=True)
        exit(1)


if __name__ == '__main__':
    import asyncio

    # time.sleep(10000)

    asyncio.run(main())
