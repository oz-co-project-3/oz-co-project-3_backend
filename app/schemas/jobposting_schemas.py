from typing import Optional

from pydantic import BaseModel

from app.models.job_posting_models import EmploymentEnum, StatusEnum


class JobPostingCreateUpdate(BaseModel):
    title: str
    location: str
    employment_type: EmploymentEnum
    position: str
    history: Optional[str] = None
    recruitment_count = int
    education: str
    deadline: str
    summary: Optional[str] = None
    description: str
    status: StatusEnum

    class Config:
        orm_mode = True


class JobPostingResponse(BaseModel):
    id: int
    title: str
    location: str
    employment_type: EmploymentEnum
    position: str
    history: Optional[str] = None
    recruitment_count: int
    education: str
    deadline: str
    salary: int
    summary: Optional[str] = None
    description: str
    status: StatusEnum
    view_count: int
    report: int

    class Config:
        orm_mode = True
