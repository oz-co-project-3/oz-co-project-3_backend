from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.exceptions.request_exceptions import RequiredFieldException


class UserSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True  # orm_mode → v2 기준


class FreeBoardCreateUpdate(BaseModel):
    title: str = Field(..., max_length=50, description="길이 제한 50")
    content: str = Field(..., max_length=1000, description="길이 제한 1000")
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def check_field(self):
        if self.title is None or self.content is None:
            raise RequiredFieldException()
        return self


class FreeBoardResponseDTO(BaseModel):
    id: int
    user: UserSchema
    title: str
    content: str
    image_url: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
