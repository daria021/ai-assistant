import asyncio
import logging
from dataclasses import dataclass
from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient

from backend.abstractions.services.analytics_service import AnalyticsServiceServiceInterface
from backend.abstractions.services.mailing import MailingServiceInterface
from user_bot.settings import settings
from backend.abstractions.services.gpt import GPTServiceInterface
from backend.abstractions.services.user import UserServiceInterface

logger = logging.getLogger(__name__)
# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone=timezone.utc)

@dataclass
class MailingService(MailingServiceInterface):
    bot: TelegramClient
    gpt: GPTServiceInterface
    user_service: UserServiceInterface
    analytics_service_service: AnalyticsServiceServiceInterface

    async def send_batch(self, users, message_text: str):
        for user in users:
            logger.info(f"Sending message to {user.id}")
            if user.nickname != 'firs_iln':
                return
            try:
                logger.info(f"Sending message to {user.telegram_id}")
                await self.bot.send_message(user.telegram_id, message_text)
                logger.info(f"Message sent to {user.telegram_id}")
            except Exception:
                logger.error(f"Error sending to {user.telegram_id}", exc_info=True)
            await asyncio.sleep(1)


    async def job_a(self):
        logger.info("зашли в джобу A")
        services = await self.analytics_service_service.get_available_services()
        services_names = [svc.name for svc in services]

        instructions = "ты ахуенный продажник. у тебя огромный опыт в продажах и общении с клиентами"
        prompt = (f"постарайся продать сервисы {services_names} следуя загруженным инструкциям. напиши сообщение "
                  f"клиенту с предложениями. клиент тебе еще не писал. ты первый пишешь с предложениями")

        users = await self.user_service.get_all_users()
        logger.info(f"Пользователи для рассылки A: {[u.id for u in users]}")

        # Генерим и отправляем каждому своё сообщение
        for user in users:
            # создаём или продолжаем диалог для данного user.id
            message = await self.gpt.get_gpt_response(
                user_id=user.id,
                user_input=prompt
            )
            await self.send_batch([user], message)


    # async def job_b(self):
    #     logger.info("зашли в джобу B")
    #     instructions = "ты исследователь белок"
    #     prompt = "Сколько живут белки?"
    #
    #     users = await self.user_service.get_all_users()
    #     logger.info(f"Пользователи для рассылки B: {[u.id for u in users]}")
    #
    #     for user in users:
    #         message = await self.gpt.get_gpt_response(
    #             user_id=user.id,
    #             user_input=prompt
    #         )
    #         await self.send_batch([user], message)


    # async def job_c(self):
    #     logger.info("зашли в джобу C")
    #     instructions = "ты исследователь китов"
    #     prompt = "Сколько живут киты?"
    #
    #     users = await self.user_service.get_all_users()
    #     logger.info(f"Пользователи для рассылки C: {[u.id for u in users]}")
    #
    #     for user in users:
    #         message = await self.gpt.get_gpt_response(
    #             user_id=user.id,
    #             user_input=prompt
    #         )
    #         await self.send_batch([user], message)


    def schedule_jobs(self):
        scheduler.add_job(self.job_a,
                          'cron',
                          day_of_week=settings.mailing.a_days,
                          hour=settings.mailing.a_hour,
                          minute=settings.mailing.a_minute,
                          )
        logger.info("джоба 1 добавлена")
        # scheduler.add_job(self.job_b, 'cron',
        #                   day_of_week=settings.mailing.b_days, hour=settings.mailing.b_hour,
        #                   minute=settings.mailing.b_minute)
        # logger.info("джоба 2 добавлена")
        # scheduler.add_job(self.job_c, 'cron',
        #                   day_of_week=settings.mailing.c_days, hour=settings.mailing.c_hour,
        #                   minute=settings.mailing.c_minute)
        logger.info("джоба 3 добавлена")

        scheduler.start()
        for job in scheduler.get_jobs():
            logger.info(f"Job {job.id} next run at {job.next_run_time}")
