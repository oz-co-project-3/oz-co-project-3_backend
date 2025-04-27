from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from app.exceptions.base_exceptions import CustomException


class UserSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True  # orm_mode → v2 기준


class FreeBoardCreateUpdate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def check_fields(self):
        if not self.title or not self.content:
            raise CustomException(
                error="필수 필드 누락", code="required_field", status_code=400
            )
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
