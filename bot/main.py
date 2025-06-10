import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ContentType
from httpx import AsyncClient
from shared.dependencies.repositories import get_proxy_repository
from shared.dependencies.services.emoji import get_emoji_service
from shared.domain.dto import CreateProxyDTO
from shared.domain.dto.emoji import CreateEmojiDTO
from shared.infrastructure.main_db import init_db

from dependencies.service.upload import get_upload_service
from settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

bot = Bot(token=settings.bot.token.get_secret_value())
dp = Dispatcher()
logger = logging.getLogger(__name__)


@dp.message(CommandStart(deep_link=True))
async def handler_start_deep(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть админку", web_app=WebAppInfo(url=settings.miniapp.url))]
    ])
    await message.answer(
        "Привет! ♡\n\nЭто админ-панель…\n\n*✧･ﾟ: *✧･ﾟ:*",
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@dp.message(CommandStart(deep_link=False))
async def handler_start_plain(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть админку", web_app=WebAppInfo(url=settings.miniapp.url))]
    ])
    await message.answer(
        "Привет! ♡\n\nЭто админ-панель…",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@dp.message(Command(commands=["add_emoji"]))
async def cmd_add_emoji(message: types.Message):
    await message.reply("📩 Пришлите ваш кастом-эмоджи-стикер.")

    @dp.message()
    async def process_sticker(msg: types.Message) -> None:
        sticker = msg.entities[0]
        if sticker.type != 'custom_emoji':
            await msg.reply("Это не эмоджи-стикер, попробуйте ещё раз.")
            return

        sticker_entity = (await bot.get_custom_emoji_stickers([sticker.custom_emoji_id]))[0]
        file = await bot.get_file(sticker_entity.file_id)
        file_path = file.file_path
        url = f"https://api.telegram.org/file/bot{settings.bot.token.get_secret_value()}/{file_path}"

        upload_service = get_upload_service()

        async with AsyncClient() as client:
            file_response = await client.get(url)
            if not file_response.is_success:
                logger.error("Unable to get file from Telegram API.")
                await msg.reply("Не удалось загрузить медиа, попробуйте еще раз")
                return

            file_content = file_response.content

        filename = await upload_service.upload(file_content, extension=file_path.split(".")[-1])
        file_public_url = upload_service.get_file_url(filename)

        name = f'{sticker_entity.emoji}_{sticker_entity.set_name}_{sticker_entity.custom_emoji_id}'
        dto = CreateEmojiDTO(
            name=name,
            img_url=file_public_url,
            custom_emoji_id=sticker.custom_emoji_id,
        )
        await get_emoji_service().create_emoji(dto)

        await msg.reply(f"✅ Эмоджи «{name}» зарегистрировано.")
        return None


@dp.message(Command(commands=["add_proxy"]))
async def cmd_add_proxy(message: types.Message):
    await message.reply("🌐 Пришлите список URL для подключения прокси. Каждый URL - на новой строке")

    @dp.message(F.content_type == ContentType.TEXT)
    async def process_proxy(msg: types.Message) -> None:
        proxies = msg.text.split()
        proxy_repository = get_proxy_repository()

        for proxy in proxies:
            proxy_dto = CreateProxyDTO(proxy_string=proxy)
            await proxy_repository.create(proxy_dto)

        current_proxies_count = await proxy_repository.get_available_proxies_count()
        await msg.reply(f"Добавлено {len(proxies)} новых прокси. Всего доступно {current_proxies_count} прокси.")


async def main():
    init_db(settings.main_db.url)
    logger.info("DB initialized")

    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
