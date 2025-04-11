from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "regions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "base_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "password" VARCHAR(80) NOT NULL,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "user_type" VARCHAR(20) NOT NULL DEFAULT 'seeker',
    "is_active" BOOL NOT NULL DEFAULT True,
    "status" VARCHAR(20) DEFAULT 'active',
    "email_verified" BOOL NOT NULL DEFAULT False,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "is_banned" BOOL NOT NULL DEFAULT False,
    "gender" VARCHAR(10) NOT NULL
);
COMMENT ON COLUMN "base_users"."password" IS '비밀번호는 최소 8자 이상이며 특수 문자를 포함';
CREATE TABLE IF NOT EXISTS "free_boards" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(50) NOT NULL,
    "content" TEXT NOT NULL,
    "image_url" VARCHAR(255),
    "view_count" INT NOT NULL DEFAULT 0,
    "user_id" INT NOT NULL REFERENCES "base_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "corporate_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "company_name" VARCHAR(255) NOT NULL,
    "business_start_date" TIMESTAMPTZ NOT NULL,
    "business_number" VARCHAR(20) NOT NULL UNIQUE,
    "company_description" TEXT,
    "manager_name" VARCHAR(100) NOT NULL,
    "manager_phone_number" VARCHAR(20) NOT NULL,
    "manager_email" VARCHAR(255) UNIQUE,
    "gender" VARCHAR(10) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "base_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "job_postings" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL UNIQUE,
    "location" VARCHAR(150) NOT NULL,
    "employment_type" VARCHAR(2) NOT NULL DEFAULT '일반',
    "position" VARCHAR(50) NOT NULL,
    "history" TEXT,
    "recruitment_count" INT NOT NULL,
    "education" VARCHAR(20) NOT NULL,
    "deadline" VARCHAR(20) NOT NULL,
    "salary" INT NOT NULL DEFAULT 0,
    "summary" TEXT,
    "description" TEXT NOT NULL,
    "status" VARCHAR(5) NOT NULL DEFAULT '모집중',
    "view_count" INT NOT NULL DEFAULT 0,
    "report" INT NOT NULL DEFAULT 0,
    "user_id" INT NOT NULL REFERENCES "corporate_users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "job_postings"."employment_type" IS 'Public: 공공\nGeneral: 일반';
COMMENT ON COLUMN "job_postings"."status" IS 'Open: 모집중\nClosing_soon: 마감 임박\nClosed: 모집 종료\nBlinded: 블라인드';
CREATE TABLE IF NOT EXISTS "reject_postings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "content" TEXT NOT NULL,
    "job_posting_id" INT NOT NULL REFERENCES "job_postings" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "base_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "seeker_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL,
    "phone_number" VARCHAR(20) NOT NULL,
    "birth" DATE,
    "interests" VARCHAR(100),
    "interests_posting" VARCHAR(255),
    "purposes" VARCHAR(100),
    "sources" VARCHAR(60),
    "applied_posting" VARCHAR(60),
    "applied_posting_count" INT NOT NULL DEFAULT 0,
    "is_social" BOOL NOT NULL DEFAULT False,
    "status" VARCHAR(20) NOT NULL DEFAULT 'seeking',
    "user_id" INT NOT NULL REFERENCES "base_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "success_reviews" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "content" TEXT NOT NULL,
    "job_title" VARCHAR(50) NOT NULL,
    "company_name" VARCHAR(50) NOT NULL,
    "employment_type" VARCHAR(3) NOT NULL DEFAULT '정규직',
    "view_count" INT NOT NULL DEFAULT 0,
    "user_id" INT NOT NULL REFERENCES "seeker_users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "success_reviews"."employment_type" IS 'REGULAR: 정규직\nCONTRACT: 계약직\nINTERN: 인턴';
CREATE TABLE IF NOT EXISTS "resumes" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "visibility" BOOL NOT NULL DEFAULT True,
    "name" VARCHAR(30) NOT NULL,
    "phone_number" VARCHAR(40) NOT NULL,
    "email" VARCHAR(50) NOT NULL,
    "image_profile" VARCHAR(255),
    "interests" VARCHAR(100),
    "desired_area" VARCHAR(50) NOT NULL,
    "education" VARCHAR(10),
    "school_name" VARCHAR(20),
    "graduation_status" VARCHAR(20),
    "introduce" TEXT NOT NULL,
    "status" VARCHAR(3) NOT NULL DEFAULT '작성중',
    "document_url" VARCHAR(255),
    "user_id" INT NOT NULL REFERENCES "seeker_users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "resumes"."status" IS 'Writing: 작성중\nSeeking: 구직중\nClosed: 완료';
CREATE TABLE IF NOT EXISTS "work_experiences" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "company" VARCHAR(30) NOT NULL,
    "period" VARCHAR(20) NOT NULL,
    "position" VARCHAR(20) NOT NULL,
    "resume_id" INT NOT NULL REFERENCES "resumes" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "comments" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "content" TEXT NOT NULL,
    "free_board_id" INT REFERENCES "free_boards" ("id") ON DELETE CASCADE,
    "success_review_id" INT REFERENCES "success_reviews" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "applicants" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(5) NOT NULL DEFAULT '지원 중',
    "job_posting_id" INT NOT NULL REFERENCES "job_postings" ("id") ON DELETE CASCADE,
    "resume_id" INT NOT NULL REFERENCES "resumes" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "base_users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "applicants"."status" IS 'Applied: 지원 중\nCancelled: 지원 취소';
CREATE TABLE IF NOT EXISTS "user_bans" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "reason" TEXT,
    "banned_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "banned_until" TIMESTAMPTZ,
    "email_sent" BOOL NOT NULL DEFAULT False,
    "banned_by_id" INT NOT NULL REFERENCES "base_users" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "base_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
