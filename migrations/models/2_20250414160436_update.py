from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chatbot" ALTER COLUMN "answer" DROP NOT NULL;
        ALTER TABLE "chatbot" ALTER COLUMN "options" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chatbot" ALTER COLUMN "answer" SET NOT NULL;
        ALTER TABLE "chatbot" ALTER COLUMN "options" SET NOT NULL;"""
