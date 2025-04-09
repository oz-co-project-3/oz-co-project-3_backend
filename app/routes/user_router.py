from fastapi import APIRouter, HTTPException

from app.schemas.user_schema import (
    CompanyRegisterRequest,
    CompanyRegisterResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.register_services import register_company_user, register_user

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register/", response_model=UserRegisterResponse, status_code=201)
async def register(request: UserRegisterRequest):
    return await register_user(request)


@router.post(
    "/register-company/", response_model=CompanyRegisterResponse, status_code=201
)
async def register_company(request: CompanyRegisterRequest):
    return await register_company_user(request)
