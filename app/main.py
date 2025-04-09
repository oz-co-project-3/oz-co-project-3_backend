from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import TORTOISE_ORM

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)
