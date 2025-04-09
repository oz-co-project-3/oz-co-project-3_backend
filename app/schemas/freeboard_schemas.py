from typing import Optional

from pydantic import BaseModel


class FreeBoardCreateUpdate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class FreeBoardResponse(BaseModel):
    id: int
    user: int
    title: str
    content: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True
