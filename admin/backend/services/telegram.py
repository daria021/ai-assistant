import logging
import re
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncGenerator, Optional, Annotated
from urllib.request import proxy_bypass

from shared.abstractions.singleton import Singleton
from telethon import TelegramClient, types
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.utils import get_peer_id

from abstractions.services.telegram import TelegramServiceInterface
from domain.models.chat import TelegramChatInfo
from services.exceptions import UnableToGetChatException, PasswordNeededException

logger = logging.getLogger(__name__)


@dataclass
class TelegramService(
    TelegramServiceInterface,
    Singleton,
):
    api_id: int
    api_hash: str
    service_session_string: str
    proxy: str
    service_bot_token: str
    use_bot_for_service: bool = False

    phone_code_hashes: dict[  # todo: possible memory leak, needs interval cleaning
        Annotated[str, 'phone'],
        tuple[
            Annotated[str, 'phone code hash'],
            Annotated[datetime, 'requested at'],
        ]
    ] = field(default_factory=dict)

    async def get_chat_info(self, invite_link: str) -> TelegramChatInfo:
        try:
            async with self.get_service_client() as client:
                chat: types.Chat = await client.get_entity(invite_link)
                chat_id = get_peer_id(chat)
                return TelegramChatInfo(
                    id=chat_id,
                    title=chat.title,
                    members_count=chat.participants_count,
                )

        except Exception as e:
            logger.error("Не удалось получить title для %s: %s", invite_link, e, exc_info=True)
            raise UnableToGetChatException

    async def send_auth_code(self, phone: str, proxy: Optional[str] = None) -> None:
        client = TelegramClient(
            phone,
            self.api_id,
            self.api_hash,
            proxy=self.parse_proxy(proxy) if proxy else None,
        )
        await client.connect()

        request = await client.send_code_request(phone)
        self.phone_code_hashes[phone] = (request.phone_code_hash, datetime.now())
        logger.info(self.phone_code_hashes)

    async def get_session_string(
            self,
            phone: str,
            code: str,
            proxy: Optional[str] = None,
            password: Optional[str] = None,
    ) -> str:
        logger.info(self.phone_code_hashes)
        client = TelegramClient(
            session=phone,
            api_id=self.api_id,
            api_hash=self.api_hash,
            proxy=self.parse_proxy(proxy) if proxy else None,
        )
        await client.connect()

        phone_code_hash = self.phone_code_hashes[phone][0]
        try:
            try:
                await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            except SessionPasswordNeededError:
                await client.sign_in(password=password)

            del self.phone_code_hashes[phone]
        except SessionPasswordNeededError:
            del self.phone_code_hashes[phone]
            raise PasswordNeededException

        string = StringSession.save(client.session)
        return string

    @asynccontextmanager
    async def get_service_client(self) -> AsyncGenerator[TelegramClient, None]:
        if self.use_bot_for_service:
            async with TelegramClient('bot', self.api_id, self.api_hash) as client:
                await client.start(self.service_bot_token)

                yield client
            return

        session = StringSession(self.service_session_string)
        async with TelegramClient(session, self.api_id, self.api_hash, proxy=self.parse_proxy(self.proxy)) as client:
            await client.start()

            yield client

    @staticmethod
    def parse_proxy(proxy_string: Optional[str] = None) -> Optional[tuple]:
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
        print(proxy)
        return proxy
