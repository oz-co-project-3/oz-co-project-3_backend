from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "job_postings" ALTER COLUMN "employment_type" TYPE VARCHAR(10) USING "employment_type"::VARCHAR(10);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "job_postings" ALTER COLUMN "employment_type" TYPE VARCHAR(2) USING "employment_type"::VARCHAR(2);"""
