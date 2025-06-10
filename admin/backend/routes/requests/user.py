from pydantic import BaseModel


class VerifyAuthCodeRequest(BaseModel):
    phone: str
    code: str
    password: str
