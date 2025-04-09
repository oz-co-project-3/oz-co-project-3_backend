from datetime import datetime

from pydantic import BaseModel


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
