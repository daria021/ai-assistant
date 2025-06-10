from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel


class UpdatePostForm(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    entities: Optional[str] = None
    image: Optional[UploadFile] = None
