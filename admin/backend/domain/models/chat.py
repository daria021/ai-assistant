from pydantic import BaseModel


class TelegramChatInfo(BaseModel):
    id: int
    title: str
    members_count: int
