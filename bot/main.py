import asyncio
import logging
import os
import pathlib
from uuid import uuid4

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
from shared.infrastructure.main_db.entities import EmojiFormat

from dependencies.service.upload import get_upload_service
from settings import settings
from utils import convert_webm_to_webp, convert_tgs_to_webm

# ——— Logging & Bot setup —————————————————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

logger.info(f'starting bot with token: {settings.bot.token.get_secret_value()}')

bot = Bot(token=settings.bot.token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())  # <-- attach FSM storage


# ——— Define our two “waiting” states —————————————————————————
class BotStates(StatesGroup):
    waiting_for_proxy = State()
    waiting_for_emoji = State()
    waiting_for_remove_emoji = State()
    waiting_for_sticker_pack = State()


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
        "Привет! ♡\n\nЭто админ-панель*✧･ﾟ: *✧･ﾟ:*\n\n"
        "Команда /add_emoji добавляет кастом-эмоджи-стикер,\n\n "
        "/add_sticker_pack добавляет весь набор стикеров.\n\n",
        "Чтобы удалить стикер жми /remove_emoji\n\n"
        "/cancel чтобы отменить действие\n\n",
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
        "Привет! ♡\n\nЭто админ-панель*✧･ﾟ: *✧･ﾟ:*\n\n"
        "Команда /add_emoji добавляет кастом-эмоджи-стикер,\n\n "
        "/add_sticker_pack добавляет весь набор стикеров.\n\n"
        "Чтобы удалить стикер жми /remove_emoji\n\n"
        "/cancel чтобы отменить действие\n\n",
        reply_markup=kb,
        disable_web_page_preview=True,
    )


@dp.message(Command(commands=["cancel"]))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await message.reply(
        "Операция отменена"
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


# ───────────── /add_emoji  ─────────────────────────────────────────
@dp.message(StateFilter(BotStates.waiting_for_emoji))
async def process_sticker(msg: types.Message, state: FSMContext):
    entities: list = msg.entities or [None]
    sticker = entities[0]
    if not sticker or sticker.type != "custom_emoji":
        return await msg.reply("Это не эмоджи-стикер, попробуйте ещё раз.")

    emoji_service = get_emoji_service()
    if await emoji_service.get_emoji_by_custom_emoji_id(sticker.custom_emoji_id):
        return await msg.reply("⚠️ Такой эмоджи уже существует.")

    # ---------- качаем оригинал ----------
    entity = (await bot.get_custom_emoji_stickers([sticker.custom_emoji_id]))[0]
    tg_file = await bot.get_file(entity.file_id)
    url = f"https://api.telegram.org/file/bot{settings.bot.token.get_secret_value()}/{tg_file.file_path}"

    async with AsyncClient() as client:
        r = await client.get(url)
        if not r.is_success:
            logger.error("TG download failed: %s", r.status_code)
            return await msg.reply("Не удалось загрузить медиа 😢 Попробуйте ещё раз.")

    ext = tg_file.file_path.rsplit(".", 1)[-1].lower()
    content = r.content

    # ---------- TGS → WEBM → WEBP ----------
    if ext == "tgs":
        temp_webm = await convert_tgs_to_webm(content)  # .tgs → .webm
        new_webp = await convert_webm_to_webp(temp_webm)  # .webm → .webp
        content = pathlib.Path(new_webp).read_bytes()
        os.remove(temp_webm)
        os.remove(new_webp)
        ext = "webp"
        emoji_format = EmojiFormat.static

    # ---------- WEBM → WEBP ----------
    elif ext == "webm":
        temp = f"/tmp/{uuid4()}.webm"
        with open(temp, "wb") as f:
            f.write(content)
        new_webp = await convert_webm_to_webp(temp)
        content = pathlib.Path(new_webp).read_bytes()
        os.remove(temp);
        os.remove(new_webp)
        ext = "webp"
        emoji_format = EmojiFormat.video

    # ---------- уже статичное изображение ----------
    else:
        emoji_format = EmojiFormat.static

    # ---------- upload & save ----------
    upload_service = get_upload_service()
    filename = await upload_service.upload(content, extension=ext)
    public_url = upload_service.get_file_url(filename)

    name = f"{entity.emoji}_{entity.set_name}_{sticker.custom_emoji_id}"
    dto = CreateEmojiDTO(
        name=name,
        img_url=public_url,
        custom_emoji_id=sticker.custom_emoji_id,
        format=emoji_format,
    )
    await emoji_service.create_emoji(dto)
    await msg.reply(f"✅ Эмоджи «{name}» зарегистрировано.")
    await state.clear()


# ——— /add_sticker_pack — ask for sticker, go into sticker_pack‐state ——————————
@dp.message(Command(commands=["add_sticker_pack"]))
async def cmd_add_sticker_pack(message: types.Message, state: FSMContext):
    await message.reply(
        "📦 Пришлите ваш кастом-эмоджи-стикер из пака — и я добавлю весь набор. (Это займет около минуты)")
    await state.set_state(BotStates.waiting_for_sticker_pack)


# ───────────── /add_sticker_pack  ─────────────────────────────────
@dp.message(StateFilter(BotStates.waiting_for_sticker_pack))
async def process_sticker_pack(msg: types.Message, state: FSMContext):
    entities: list = msg.entities or [None]
    sticker = entities[0]
    if not sticker or sticker.type != "custom_emoji":
        await msg.reply("Это не эмоджи-стикер, попробуйте ещё раз.")
        return await state.clear()

    entity = (await bot.get_custom_emoji_stickers([sticker.custom_emoji_id]))[0]
    pack_name = entity.set_name
    sticker_set = await bot.get_sticker_set(pack_name)

    upload_service = get_upload_service()
    added, doubles, failed = 0, 0, 0

    all_ids = [st.custom_emoji_id for st in sticker_set.stickers]
    emoji_service = get_emoji_service()
    existing_ids = await emoji_service.get_existing_custom_ids(all_ids)

    for st in sticker_set.stickers:
        if st.custom_emoji_id in existing_ids:
            doubles += 1
            continue

        tg_file = await bot.get_file(st.file_id)
        url = f"https://api.telegram.org/file/bot{settings.bot.token.get_secret_value()}/{tg_file.file_path}"
        async with AsyncClient() as client:
            r = await client.get(url)
            if not r.is_success:
                failed += 1
                continue

        ext = tg_file.file_path.rsplit(".", 1)[-1].lower()
        content = r.content

        # ----- tgs → webm → webp -----
        if ext == "tgs":
            temp_webm = await convert_tgs_to_webm(content)
            new_webp = await convert_webm_to_webp(temp_webm)
            content = pathlib.Path(new_webp).read_bytes()
            ext = "webp"
            os.remove(temp_webm)
            os.remove(new_webp)
        # ----- webm → webp -----
        elif ext == "webm":
            logger.info(f"ext: {ext}")
            temp = f"/tmp/{uuid4()}.webm"
            with open(temp, "wb") as f:
                f.write(content)

            new_webp = await convert_webm_to_webp(temp)
            content = pathlib.Path(new_webp).read_bytes()
            ext = "webp"
            os.remove(temp)
            os.remove(new_webp)

        filename = await upload_service.upload(content, extension=ext)
        public_url = upload_service.get_file_url(filename)

        name = f"{st.emoji}_{entity.set_name}_{st.custom_emoji_id}"
        dto = CreateEmojiDTO(
            name=name,
            img_url=public_url,
            custom_emoji_id=st.custom_emoji_id,
            format=EmojiFormat.video if ext == "webm" else EmojiFormat.static,
        )
        await emoji_service.create_emoji(dto)
        added += 1

    await msg.reply(
        f"✅ Добавлено {added} стикеров (всего {added + failed + doubles}) из пака «{sticker_set.title}».\n"
        f"Ошибок загрузки: {failed}\n"
        f"Дубликатов: {doubles}"
    )
    await state.clear()


# remove added emoji
@dp.message(Command(commands=["remove_emoji"]))
async def cmd_remove_emoji(message: types.Message, state: FSMContext):
    await message.reply("📩 Пришлите кастом-эмоджи-стикер, который нужно удалить")
    await state.set_state(BotStates.waiting_for_remove_emoji)


@dp.message(
    StateFilter(BotStates.waiting_for_remove_emoji),
)
async def process_remove_sticker(msg: types.Message, state: FSMContext):
    entities: list = msg.entities or [None]
    sticker = entities[0]
    if not sticker or not sticker.type == "custom_emoji":
        return await msg.reply("Это не эмоджи-стикер, попробуйте ещё раз.")

    custom_emoji_id = sticker.custom_emoji_id
    emoji_service = get_emoji_service()
    emoji = await emoji_service.get_emoji_by_custom_emoji_id(custom_emoji_id)
    if not emoji:
        await msg.reply(f"Такого эмоджи у меня нет :(")
        return

    await emoji_service.remove_added_emoji(emoji.id)
    await msg.reply(f"✅ Эмоджи «{emoji.name}» удалено.")
    await state.clear()


# ——— bootstrap & run ——————————————————————————————————————
async def main():
    init_db(settings.main_db.url)
    logger.info("DB initialized")
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
