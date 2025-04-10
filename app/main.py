from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app.api.routes import user
from app.api.routes.freeboard import free_board_router
from app.api.routes.success_review import success_review_router
from app.api.routes.user import router as user_router
from app.core.config import TORTOISE_ORM
from app.utils.exception import CustomException

app = FastAPI()

app.include_router(user_router)


app.include_router(success_review_router)
app.include_router(free_board_router)


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
