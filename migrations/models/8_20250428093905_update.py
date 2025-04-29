from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'chatbot' AND column_name = 'url'
            ) THEN
                ALTER TABLE "chatbot" ADD "url" VARCHAR(255);
            END IF;
        END
        $$;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chatbot" DROP COLUMN IF EXISTS "url";
    """
