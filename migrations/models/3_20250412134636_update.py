from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "comments" ADD "user_id" INT NOT NULL;
        ALTER TABLE "comments" ADD CONSTRAINT "fk_comments_base_use_2bb86e06" FOREIGN KEY ("user_id") REFERENCES "base_users" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "comments" DROP CONSTRAINT IF EXISTS "fk_comments_base_use_2bb86e06";
        ALTER TABLE "comments" DROP COLUMN "user_id";"""
