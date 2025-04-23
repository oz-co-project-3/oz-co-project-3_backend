from typing import List, Optional

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int


class JobPostingResponseDTO(BaseModel):
    id: int
    user: UserSchema
    company: str
    title: str
    location: str
    employment_type: str
    employ_method: str
    work_time: str
    position: str
    history: str
    recruitment_count: int
    education: str
    deadline: str
    salary: str
    summary: str
    description: str
    status: str
    view_count: int
    report: int

    class Config:
        from_attributes = True


class ApplicantCreateUpdateSchema(BaseModel):
    resume: int
    status: str
    memo: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicantResponseDTO(BaseModel):
    id: int
    job_posting: int
    resume: int
    user: int
    status: str
    memo: Optional[str]

    class Config:
        from_attributes = True


class PaginatedJobPostingsResponseDTO(BaseModel):
    total: int
    offset: int
    limit: int
    data: List[JobPostingResponseDTO]

    class Config:
        from_attributes = True
