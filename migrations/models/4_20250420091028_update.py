from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" ADD "leave_reason" TEXT;
        ALTER TABLE "base_users" ALTER COLUMN "user_type" TYPE VARCHAR(20) USING "user_type"::VARCHAR(20);
        COMMENT ON COLUMN "base_users"."user_type" IS 'SEEKER: seeker
BUSINESS: business';
        COMMENT ON COLUMN "base_users"."password" IS NULL;
        ALTER TABLE "base_users" ALTER COLUMN "gender" TYPE VARCHAR(10) USING "gender"::VARCHAR(10);
        COMMENT ON COLUMN "base_users"."gender" IS 'MALE: male
FEMALE: female';
        ALTER TABLE "base_users" ALTER COLUMN "status" SET NOT NULL;
        ALTER TABLE "base_users" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
        COMMENT ON COLUMN "base_users"."status" IS 'ACTIVE: active
SUSPEND: suspend
DELETE: delete
PENDING: pending';
        ALTER TABLE "corporate_users" ADD "profile_url" VARCHAR(255);
        ALTER TABLE "corporate_users" ALTER COLUMN "gender" TYPE VARCHAR(10) USING "gender"::VARCHAR(10);
        COMMENT ON COLUMN "corporate_users"."gender" IS 'MALE: male
FEMALE: female';
        ALTER TABLE "seeker_users" ADD "profile_url" VARCHAR(255);
        ALTER TABLE "seeker_users" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
        COMMENT ON COLUMN "seeker_users"."status" IS 'SEEKING: seeking
EMPLOYED: employed
NOT_SEEKING: not_seeking';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "base_users" DROP COLUMN "leave_reason";
        ALTER TABLE "base_users" ALTER COLUMN "user_type" TYPE VARCHAR(20) USING "user_type"::VARCHAR(20);
        COMMENT ON COLUMN "base_users"."user_type" IS NULL;
        COMMENT ON COLUMN "base_users"."password" IS '비밀번호는 최소 8자 이상이며 특수 문자를 포함';
        ALTER TABLE "base_users" ALTER COLUMN "gender" TYPE VARCHAR(10) USING "gender"::VARCHAR(10);
        COMMENT ON COLUMN "base_users"."gender" IS NULL;
        ALTER TABLE "base_users" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
        ALTER TABLE "base_users" ALTER COLUMN "status" DROP NOT NULL;
        COMMENT ON COLUMN "base_users"."status" IS NULL;
        ALTER TABLE "seeker_users" DROP COLUMN "profile_url";
        ALTER TABLE "seeker_users" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
        COMMENT ON COLUMN "seeker_users"."status" IS NULL;
        ALTER TABLE "corporate_users" DROP COLUMN "profile_url";
        ALTER TABLE "corporate_users" ALTER COLUMN "gender" TYPE VARCHAR(10) USING "gender"::VARCHAR(10);
        COMMENT ON COLUMN "corporate_users"."gender" IS NULL;"""
