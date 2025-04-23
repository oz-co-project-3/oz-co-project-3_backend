from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from tortoise.contrib.fastapi import register_tortoise

from app.api.v1.admin import admin_router
from app.api.v1.chatbot import chatbot_router
from app.api.v1.comment import comment_router
from app.api.v1.freeboard import free_board_router
from app.api.v1.jobposting import job_posting_router
from app.api.v1.postings import posting_router
from app.api.v1.public_api import public_router
from app.api.v1.resume import resume_router
from app.api.v1.success_review import success_review_router
from app.api.v1.user import router as user_router
from app.api.v1.websocket import websocket_router
from app.core.config import TORTOISE_ORM
from app.utils.exception import CustomException

bearer_scheme = HTTPBearer()
app = FastAPI()

app.include_router(user_router)
app.include_router(comment_router)
app.include_router(success_review_router)
app.include_router(free_board_router)
app.include_router(admin_router)
app.include_router(job_posting_router)
app.include_router(chatbot_router)
app.include_router(websocket_router)
app.include_router(posting_router)
app.include_router(public_router)
app.include_router(resume_router)

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
        title="My API",
        version="1.0.0",
        description="This is my API",
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
