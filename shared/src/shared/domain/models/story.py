from typing import Optional

from pydantic import ConfigDict

from .abstract import Model


class Story(Model):
    name: str
    file_path: str
    text: Optional[str]

    model_config = ConfigDict(from_attributes=True)
