from pydantic import ConfigDict

from .abstract import Model


class Service(Model):
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
