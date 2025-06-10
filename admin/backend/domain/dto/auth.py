from pydantic import BaseModel, SecretStr, field_serializer, Field


class Credentials(BaseModel):
    username: str
    password: str


class AuthTokens(BaseModel):
    access_token: SecretStr = Field(..., serialization_alias='accessToken')
    refresh_token: SecretStr = Field(..., serialization_alias='refreshToken')

    @field_serializer('access_token', 'refresh_token')
    def dump_secret(self, v):
        return v.get_secret_value()
