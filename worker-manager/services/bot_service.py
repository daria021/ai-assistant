import logging
from aiogram import Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# from aiogram.client.session import SessionMiddleware

from abstractions.services.bot_service import BotServiceInterface
from dependencies.services.upload import get_upload_service
from settings import settings

logger = logging.getLogger(__name__)

class AiogramBotService(BotServiceInterface):
    def __init__(self):
        token = settings.posting_bot.token.get_secret_value()
        # устанавливаем HTML-парсинг по умолчанию
        default_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
        self.bot = Bot(
            token=token,
            default=default_props,
            # при желании можно явно попросить бот сам закрыть сессию в деструкторе
            # auto_close=True,
        )
        self.upload = get_upload_service()

    async def send_post(
            self,
            chat_id: int,
            text: str,
            entities: list = None,
            media_path: str = None,
    ) -> None:
        """
        Отправляем либо текст, либо фото+текст пользователю/каналу.
        Поддержка платных эмоджи: просто встраиваются в text.
        """
        # 1) Логируем исходные entities перед любой обработкой
        logger.debug("BOT_BUILD raw_entities=%s", entities[:8])

        if media_path:
            logger.info(f"BotService: send_photo to {chat_id}")
            media_url = self.upload.get_file_url(media_path)
            logger.info(media_url)
            logger.info(media_path)
            logger.info(settings.environment.host)

            # 2) Проверяем offsets прямо перед отправкой фото
            bad = []
            for ent in entities or []:
                offset = ent["offset"]
                length = ent["length"]
                frag = text[offset: offset + length]
                if frag != "🦏":
                    bad.append((offset, repr(frag)))
            logger.debug(
                "BOT_SEND_PHOTO text=%r ENT(first8)=%s BAD(first5)=%s",
                text[:200],
                entities[:8],
                bad[:5],
            )

            await self.bot.send_photo(
                chat_id,
                photo=media_url,
                caption=text,
                caption_entities=entities,
            )
        else:
            logger.info(f"BotService: send_message to {chat_id}")

            # 3) Проверяем offsets прямо перед отправкой текста
            bad = []
            for ent in entities or []:
                offset = ent["offset"]
                length = ent["length"]
                frag = text[offset: offset + length]
                if frag != "🦏":
                    bad.append((offset, repr(frag)))
            logger.debug(
                "BOT_SEND_TEXT text=%r ENT(first8)=%s BAD(first5)=%s",
                text[:200],
                entities[:8],
                bad[:5],
            )

            await self.bot.send_message(
                chat_id,
                text,
                entities=entities,
            )
