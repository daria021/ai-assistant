from abc import ABC

from telethon import TelegramClient

from backend.abstractions.services.gpt import GPTServiceInterface
from backend.abstractions.services.user import UserServiceInterface


class MailingServiceInterface(ABC):
    bot: TelegramClient
    gpt: GPTServiceInterface
    user_service: UserServiceInterface

    async def send_batch(self, users, message_text: str):
        ...

    async def job_a(self):
        ...

    async def job_b(self):
        ...

    async def job_c(self):
        ...

    def schedule_jobs(self):
        ...