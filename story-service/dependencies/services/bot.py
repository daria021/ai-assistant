from telethon import TelegramClient

from user_bot import bot


def get_bot() -> TelegramClient:
    return bot
