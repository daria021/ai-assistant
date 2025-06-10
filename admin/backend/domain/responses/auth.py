from pydantic import BaseModel, Field


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
