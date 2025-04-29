from typing import Optional

from pydantic import BaseModel, Field


class ChatBotCreateUpdate(BaseModel):
    step: int = Field(..., le=10)
    is_terminate: bool
    selection_path: str = Field(..., max_length=50, description="50자 제한")
    options: Optional[str] = Field(None, max_length=50, description="50자 제한")
    answer: Optional[str] = Field(None, max_length=150, description="100자 제한")
    url: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class ChatBotResponseDTO(BaseModel):
    id: int
    step: int
    is_terminate: bool
    selection_path: str
    options: Optional[str] = None
    answer: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True
