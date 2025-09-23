#!/usr/bin/env python3
"""
Простой скрипт для отправки тестового сообщения в Telegram
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession


async def send_test_message():
    # Настройки - замените на свои
    api_id = 12345678  # Ваш API ID
    api_hash = 'your_api_hash_here'  # Ваш API Hash

    # Либо используйте session string (если есть)
    session_string = None  # Или укажите session string если есть

    # ID чата куда отправить сообщение (ваш личный чат)
    # Можно получить через @userinfobot или в логах
    chat_id = 123456789  # Ваш Telegram ID

    # Создаем клиент
    if session_string:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
    else:
        # Если нет session string, будет запрошена авторизация
        client = TelegramClient('test_session', api_id, api_hash)

    try:
        print("Подключаемся к Telegram...")
        await client.start()

        print("Отправляем тестовое сообщение...")
        await client.send_message(chat_id, "Тестовое сообщение от скрипта! 🚀")

        print("✅ Сообщение отправлено успешно!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(send_test_message())
