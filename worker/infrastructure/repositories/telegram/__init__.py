import logging
import re
from asyncio import IncompleteReadError
from dataclasses import dataclass
from typing import Optional, Any

from shared.domain.dto.post_to_publish import MessageEntityDTO
from telethon import TelegramClient as Client
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import (
    MessageEntityCustomEmoji,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityUnderline,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityBlockquote,   # ← добавили
    TypeMessageEntity
)

from abstractions.repositories import TelegramMessagesRepositoryInterface
from shared.domain.models import UserWithSessionString

from dependencies.services.upload import get_upload_service
from settings import settings
from .exceptions import ChatJoinError, UnhandlableError

logger = logging.getLogger(__name__)
client_logger = logger.getChild("client")
client_logger.setLevel(logging.ERROR)


@dataclass
class TelethonTelegramMessagesRepository(
    TelegramMessagesRepositoryInterface,
):
    api_id: int
    api_hash: str

    worker: UserWithSessionString

    async def join_chat(self, chat: str | int):
        logger.info(f"Joining chat {chat} with bot {self.worker.telegram_username} ({self.worker.id})")

        client = Client(
            session=StringSession(self.worker.session_string),
            api_id=self.api_id,
            api_hash=self.api_hash,
            base_logger=client_logger,
        )

        await client.connect()
        try:
            entity = await client.get_entity(chat)

            await client(JoinChannelRequest(entity))  # noqa
            await client.disconnect()
        except Exception as e:
            await client.disconnect()
            raise ChatJoinError(
                f"There is an error joining chat {chat} with bot {self.worker.telegram_username} ({self.worker.id}):"
                f" {type(e).__name__}: {e}"
            )

    async def send_message(
            self,
            chat_id: int,
            text: str,
            entities: Optional[list[MessageEntityDTO]] = None,
            media_path: Optional[str] = None,
            reply_to: Optional[int] = None,
            retry: int = 0,
    ) -> int:
        if not self.api_id or not self.api_hash or not self.worker.session_string:
            logger.info(
                f"One of required parameters "
                f"(api_id={self.api_id}, api_hash={self.api_hash}, "
                f"worker={self.worker.session_string[:5]}...{self.worker.session_string[-5:]}) "
                f"is missing, aborting sending message"
            )
            raise ValueError("api_id, api_hash and session_string are required")

        client = Client(
            session=StringSession(self.worker.session_string),
            api_id=self.api_id,
            api_hash=self.api_hash,
            base_logger=client_logger,
            proxy=self.parse_proxy(self.worker.proxy.proxy_string) if self.worker.proxy else None,
            auto_reconnect=True,
        )

        try:
            await client.connect()
            logger.info("Client connected")

            sending_args: dict[str, Any] = {
                "entity": chat_id,
                "message": text,
            }

            if reply_to:
                sending_args['reply_to'] = reply_to

            if media_path:
                upload_service = get_upload_service()
                logger.info(f"Uploading file {media_path}")
                sending_args['file'] = upload_service.get_file_url(media_path)
                logger.info(f"File path: {sending_args['file']}")

            if entities:
                entities_to_send = self._prepare_entities(entities)
                sending_args['formatting_entities'] = entities_to_send
                logger.info(
                    f"TELETHON_SEND text={sending_args.get("message", "")[:200]} "
                    f"ENT={sending_args.get('formatting_entities', [])[:8]}",
                )
                sending_args['link_preview'] = False

            logger.info(f"Sending {sending_args}")
            message = await client.send_message(**sending_args)
            logger.info('Message sent')

            await client.disconnect()
            logger.info("Client disconnected")
            return message.id
        except (RuntimeError, IncompleteReadError, ConnectionResetError) as e:
            try:
                await client.disconnect()
            except:
                pass

            if retry > 5:
                logger.error("Cannot connect to Telegram")
                raise UnhandlableError from e

            return await self.send_message(
                chat_id=chat_id,
                text=text,
                reply_to=reply_to,
                retry=retry + 1,
            )

    @staticmethod
    def parse_proxy(proxy_string: Optional[str]) -> Optional[tuple]:
        if not proxy_string:
            return

        # Regex to parse the proxy string
        pattern = re.compile(
            r"^(?P<protocol>http|socks5|socks4)://(?P<username>.+?):(?P<password>.+?)@(?P<host>.+?):(?P<port>\d+)$"
        )
        match = pattern.match(proxy_string)
        if not match:
            raise ValueError("Invalid proxy format")

        # Extracting components
        components = match.groupdict()
        protocol = components["protocol"]
        username = components["username"]
        password = components["password"]
        host = components["host"]
        port = int(components["port"])

        # Map protocol to PySocks format
        proxy_type = {
            "http": "HTTP",
            "socks5": "SOCKS5",
            "socks4": "SOCKS4"
        }.get(protocol, None)

        if not proxy_type:
            raise ValueError("Unsupported proxy protocol")

        # PySocks/Telethon-compatible format
        proxy = (proxy_type, host, port, True, username, password)
        return proxy

    @staticmethod
    def _prepare_entities(raw_entities: list[MessageEntityDTO]) -> list[TypeMessageEntity]:
        entities = []
        for raw_entity in raw_entities:
            match raw_entity.type:
                case "custom_emoji":
                    entity_to_add = MessageEntityCustomEmoji(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                        document_id=raw_entity.custom_emoji_id,
                    )
                    entities.append(entity_to_add)
                case 'bold':
                    entity_to_add = MessageEntityBold(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                    )
                    entities.append(entity_to_add)
                case 'italic':
                    entity_to_add = MessageEntityItalic(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                    )
                    entities.append(entity_to_add)
                case 'underline':
                    entity_to_add = MessageEntityUnderline(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                    )
                    entities.append(entity_to_add)
                case 'strikethrough':
                    entity_to_add = MessageEntityStrike(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                    )
                    entities.append(entity_to_add)
                case 'text_link':
                    entity_to_add = MessageEntityTextUrl(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                        url=raw_entity.url,
                    )
                    entities.append(entity_to_add)
                case 'blockquote':                                  # ← добавили
                    entity_to_add = MessageEntityBlockquote(
                        offset=raw_entity.offset,
                        length=raw_entity.length,
                    )
                    entities.append(entity_to_add)

        return entities
