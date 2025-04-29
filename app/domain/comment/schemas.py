from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreateUpdateSchema(BaseModel):
    content: str


class CommentResponseDTO(BaseModel):
    id: int
    content: str = Field(..., max_length=200, description="길이 제한 100자")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
