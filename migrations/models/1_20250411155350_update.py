from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "job_postings" ADD "company" VARCHAR(50) NOT NULL;
        COMMENT ON COLUMN "job_postings"."status" IS 'Open: 모집중
Closing_soon: 마감 임박
Closed: 모집 종료
Blinded: 블라인드
Pending: 대기중
Rejected: 반려됨';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "job_postings" DROP COLUMN "company";
        COMMENT ON COLUMN "job_postings"."status" IS 'Open: 모집중
Closing_soon: 마감 임박
Closed: 모집 종료
Blinded: 블라인드';"""
