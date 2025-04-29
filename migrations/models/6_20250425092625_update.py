from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "resumes" RENAME COLUMN "image_profile" TO "image_url";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "resumes" RENAME COLUMN "image_url" TO "image_profile";"""
