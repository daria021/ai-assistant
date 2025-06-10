from pydantic import BaseModel


class CreateProxyRequest(BaseModel):
    urls: list[str]
