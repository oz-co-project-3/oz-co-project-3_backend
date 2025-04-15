from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int


class JobPostingResponse(BaseModel):
    id: int
    user: UserSchema
    company: str
    title: str
    location: str
    employment_type: str
    position: str
    history: str
    recruitment_count: int
    education: str
    deadline: str
    salary: int
    summary: str
    description: str
    status: str
    view_count: int
    report: int
