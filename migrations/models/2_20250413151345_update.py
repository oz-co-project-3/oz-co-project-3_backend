from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ALTER COLUMN "status" SET DEFAULT 'pending';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ALTER COLUMN "status" SET DEFAULT 'active';"""
