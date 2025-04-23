from datetime import datetime

from pydantic import BaseModel, model_validator

from app.domain.services.verification import CustomException


class UserSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True


class SuccessReviewCreateUpdateSchema(BaseModel):
    title: str
    content: str
    job_title: str
    company_name: str
    employment_type: str

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def check_fields(self):
        if (
            not self.title
            or not self.content
            or not self.job_title
            or not self.company_name
            or not self.employment_type
        ):
            raise CustomException(
                error="필수 필드 누락", code="required_field", status_code=400
            )
        return self


class SuccessReviewResponseSchema(BaseModel):
    id: int
    user: UserSchema
    title: str
    content: str
    job_title: str
    company_name: str
    employment_type: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
