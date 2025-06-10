from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    invite_link: str