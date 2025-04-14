from typing import Optional

from pydantic import BaseModel


class ChatBotCreateUpdate(BaseModel):
    step: int
    is_terminate: bool
    selection_path: str
    options: Optional[str] = None
    answer: Optional[str] = None

    class Config:
        from_attributes = True


class ChatBotResponseSchema(BaseModel):
    id: int
    step: int
    is_terminate: bool
    selection_path: str
    options: Optional[str] = None
    answer: Optional[str] = None

    class Config:
        from_attributes = True
