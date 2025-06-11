import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    ContentType,
)
from httpx import AsyncClient
from shared.dependencies.repositories import get_proxy_repository
from shared.dependencies.services.emoji import get_emoji_service
from shared.domain.dto import CreateProxyDTO
from shared.domain.dto.emoji import CreateEmojiDTO
from shared.infrastructure.main_db import init_db

from dependencies.service.upload import get_upload_service
from settings import settings

# ——— Logging & Bot setup —————————————————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot.token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())  # <-- attach FSM storage


# ——— Define our two “waiting” states —————————————————————————
class BotStates(StatesGroup):
    waiting_for_proxy = State()
    waiting_for_emoji = State()


# ——— /start handlers (unchanged) ————————————————————————————
@dp.message(CommandStart(deep_link=True))
async def handler_start_deep(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть админку",
                    web_app=WebAppInfo(url=settings.miniapp.url),
                )
            ]
        ]
    )
    await message.answer(
        "Привет! ♡\n\nЭто админ-панель…\n\n*✧･ﾟ: *✧･ﾟ:*",
        reply_markup=kb,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@dp.message(CommandStart(deep_link=False))
async def handler_start_plain(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть админку",
                    web_app=WebAppInfo(url=settings.miniapp.url),
                )
            ]
        ]
    )
    await message.answer(
        "Привет! ♡\n\nЭто админ-панель…",
        reply_markup=kb,
        disable_web_page_preview=True,
    )


# ——— /add_proxy — ask for text, go into proxy‐state —————————————
@dp.message(Command(commands=["add_proxy"]))
async def cmd_add_proxy(message: types.Message, state: FSMContext):
    await message.reply(
        "🌐 Пришлите список URL для подключения прокси. Каждый URL – на новой строке"
    )
    await state.set_state(BotStates.waiting_for_proxy)


# ——— proxy‐state handler: only text, only in waiting_for_proxy —————
@dp.message(
    StateFilter(BotStates.waiting_for_proxy),
    F.content_type == ContentType.TEXT,
)
async def process_proxy(msg: types.Message, state: FSMContext):
    proxies = msg.text.split()
    repo = get_proxy_repository()
    for proxy in proxies:
        dto = CreateProxyDTO(proxy_string=proxy)
        await repo.create(dto)
    total = await repo.get_available_proxies_count()
    await msg.reply(f"Добавлено {len(proxies)} новых прокси. Всего доступно {total} прокси.")
    await state.clear()  # done with proxies


# ——— /add_emoji — ask for sticker, go into emoji‐state ——————————
@dp.message(Command(commands=["add_emoji"]))
async def cmd_add_emoji(message: types.Message, state: FSMContext):
    await message.reply("📩 Пришлите ваш кастом-эмоджи-стикер.")
    await state.set_state(BotStates.waiting_for_emoji)


# ——— emoji‐state handler: only stickers, only in waiting_for_emoji ——
@dp.message(
    StateFilter(BotStates.waiting_for_emoji),
)
async def process_sticker(msg: types.Message, state: FSMContext):
    entities: list = msg.entities or [None]
    sticker = entities[0]
    if not sticker or not sticker.type == "custom_emoji":
        return await msg.reply("Это не эмоджи-стикер, попробуйте ещё раз.")

    # download the file from Telegram
    entity = (await bot.get_custom_emoji_stickers([sticker.custom_emoji_id]))[0]
    file = await bot.get_file(entity.file_id)
    url = f"https://api.telegram.org/file/bot{settings.bot.token.get_secret_value()}/{file.file_path}"
    upload_service = get_upload_service()

    async with AsyncClient() as client:
        resp = await client.get(url)
        if not resp.is_success:
            logger.error("Unable to fetch sticker from Telegram: %s", resp.status_code)
            return await msg.reply("Не удалось загрузить медиа, попробуйте ещё раз.")

    ext = file.file_path.rsplit(".", 1)[-1]
    filename = await upload_service.upload(resp.content, extension=ext)
    public_url = upload_service.get_file_url(filename)

    name = f"{entity.emoji}_{entity.set_name}_{sticker.custom_emoji_id}"
    dto = CreateEmojiDTO(
        name=name,
        img_url=public_url,
        custom_emoji_id=sticker.custom_emoji_id,
    )
    await get_emoji_service().create_emoji(dto)

    await msg.reply(f"✅ Эмоджи «{name}» зарегистрировано.")
    await state.clear()  # done with emoji


# ——— bootstrap & run ——————————————————————————————————————
async def main():
    init_db(settings.main_db.url)
    logger.info("DB initialized")
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
