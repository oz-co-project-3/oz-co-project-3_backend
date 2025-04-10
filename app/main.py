from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from tortoise.contrib.fastapi import register_tortoise

from app.api.routes.admin.admin_user import admin_router
from app.api.routes.freeboard import free_board_router
from app.api.routes.success_review import success_review_router
from app.api.routes.user import router as user_router
from app.core.config import TORTOISE_ORM
from app.utils.exception import CustomException

bearer_scheme = HTTPBearer()
app = FastAPI()

app.include_router(user_router)

app.include_router(success_review_router)
app.include_router(free_board_router)
app.include_router(admin_router)


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
