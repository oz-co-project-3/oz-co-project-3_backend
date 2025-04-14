from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" DROP COLUMN "is_banned";
        ALTER TABLE "base_users" DROP COLUMN "is_active";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ADD "is_banned" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "base_users" ADD "is_active" BOOL NOT NULL DEFAULT True;"""
