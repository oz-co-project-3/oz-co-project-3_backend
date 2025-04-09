from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import TORTOISE_ORM
from app.routes import user_router
from app.utils.exception import CustomException

app = FastAPI()

app.include_router(user_router.router)


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
