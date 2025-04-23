from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentCreateUpdateSchema(BaseModel):
    content: str


class CommentResponseDTO(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
