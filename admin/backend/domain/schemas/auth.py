from pydantic import BaseModel


class Credentials(BaseModel):
    auth_code: str

class Tokens(BaseModel):
    access_token: str
