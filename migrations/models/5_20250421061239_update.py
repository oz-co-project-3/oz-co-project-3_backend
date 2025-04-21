from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "job_postings" ADD "career" VARCHAR(10) NOT NULL DEFAULT '경력무관';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "job_postings" DROP COLUMN "career";"""
