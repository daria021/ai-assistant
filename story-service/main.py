import logging

from backend.dependencies.services.bot import get_bot
from backend.dependencies import get_mailing_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = get_bot()


async def main():
    mailing = get_mailing_service()
    mailing.schedule_jobs()

    print('Бот и шедулер запущены...')
    await bot.run_until_disconnected()

    print("Бот остановлен")


if __name__ == '__main__':
    bot.loop.run_until_complete(main())
