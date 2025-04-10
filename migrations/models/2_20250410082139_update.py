from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ADD "is_admin" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "seeker_users" ADD "birth" DATE;
        ALTER TABLE "seeker_users" DROP COLUMN "age";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" DROP COLUMN "is_admin";
        ALTER TABLE "seeker_users" ADD "age" INT NOT NULL;
        ALTER TABLE "seeker_users" DROP COLUMN "birth";"""
