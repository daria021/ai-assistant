import logging
from aiogram import Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# from aiogram.client.session import SessionMiddleware

from abstractions.services.bot_service import BotServiceInterface
from dependencies.services.upload import get_upload_service
from settings import settings

from aiogram.types import (
    MessageEntityCustomEmoji,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityText,
)

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

    def _build_entities(self, raw_entities: list[dict] | None) -> list:
        """Преобразует JSON-список из БД в список Aiogram MessageEntity."""
        result: list = []
        if not raw_entities:
            return result

        for e in raw_entities:
            typ = e.get("type")
            if typ == "custom_emoji":
                result.append(MessageEntityCustomEmoji(
                    offset=e["offset"],
                    length=e["length"],
                    custom_emoji_id=e["custom_emoji_id"],
                ))
            elif typ == "bold":
                result.append(MessageEntityBold(
                    offset=e["offset"],
                    length=e["length"],
                ))
            elif typ == "italic":
                result.append(MessageEntityItalic(
                    offset=e["offset"],
                    length=e["length"],
                ))
            else:
                # чтобы не ломать смещения, вкладываем “текстовую” сущность
                result.append(MessageEntityText(
                    offset=e["offset"],
                    length=e["length"],
                ))
        return result


    async def send_post(
        self,
        chat_id: int,
        text: str,
        entities: list = None,
        media_path: str = None,
    ) -> None:

        parsed_entities = self._build_entities(entities)

        if media_path:
            logger.info(f"BotService: send_photo to {chat_id}")
            media_url = self.upload.get_file_url(media_path)
            logger.info(media_url)
            logger.info(media_path)
            logger.info(settings.environment.host)
            logger.info(text)
            logger.info(entities)
            await self.bot.send_photo(chat_id, photo=media_url, caption=text, caption_entities=parsed_entities)
        else:
            logger.info(f"BotService: send_message to {chat_id}")
            await self.bot.send_message(chat_id, text, entities=parsed_entities)
