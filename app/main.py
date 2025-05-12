import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from tortoise.contrib.fastapi import register_tortoise
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api.v1.admin import admin_router
from app.api.v1.applicant import applicant_router
from app.api.v1.chatbot import chatbot_router
from app.api.v1.comment import comment_router
from app.api.v1.freeboard import free_board_router
from app.api.v1.jobposting import job_posting_router
from app.api.v1.postings import posting_router
from app.api.v1.resume import resume_router
from app.api.v1.success_review import success_review_router
from app.api.v1.user import router as user_router
from app.api.v1.websocket import websocket_router
from app.core.config import TORTOISE_ORM
from app.core.settings import settings
from app.domain.services.s3_service import image_upload_router
from app.exceptions.base_exceptions import CustomException

bearer_scheme = HTTPBearer()
app = FastAPI(
    # docs_url=None if settings.ENV == "prod" else "/docs",
    # redoc_url=None if settings.ENV == "prod" else "/redoc",
    # openapi_url=None if settings.ENV == "prod" else "/openapi.json",
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.include_router(user_router)
app.include_router(comment_router)
app.include_router(success_review_router)
app.include_router(free_board_router)
app.include_router(admin_router)
app.include_router(job_posting_router)
app.include_router(chatbot_router)
app.include_router(websocket_router)
app.include_router(posting_router)
app.include_router(resume_router)
app.include_router(image_upload_router)
app.include_router(applicant_router)

if settings.ENV == "prod":
    origins = [
        "https://senior-tomorrow.o-r.kr",  # 실제 서비스 도메인
    ]
else:
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 위에서 지정한 origins 목록 허용
    allow_credentials=True,  # 쿠키 포함 요청 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": {
                "error": exc.error,
                "code": exc.code,
            }
        },
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Senior-tomorrow",
        version="1.0.0",
        description=(
            """
            Senior-tomorrow API 문서입니다.\n\n
            - 시니어를 위한 구인/구직 서비스를 지원합니다.\n
            - 프론트엔드 및 외부 서비스 연동을 위해 사용됩니다.\n
            - 로그인, 공고 조회를 제외한 모든 API는 Bearer JWT 인증을 필요로 합니다.\n
            - 버전: v1.0.0
            """
        ),
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


logging.basicConfig(
    level=logging.INFO,  # 출력할 최소 레벨: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
