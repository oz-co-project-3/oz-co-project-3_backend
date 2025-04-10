from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ALTER COLUMN "password" TYPE VARCHAR(80) USING "password"::VARCHAR(80);
        ALTER TABLE "corporate_users" ADD "gender" VARCHAR(10) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ALTER COLUMN "password" TYPE VARCHAR(20) USING "password"::VARCHAR(20);
        ALTER TABLE "corporate_users" DROP COLUMN "gender";"""
