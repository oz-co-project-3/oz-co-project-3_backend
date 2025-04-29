from unittest.mock import AsyncMock, patch

import pytest

from app.domain.admin.schemas.job_posting_schemas import (
    EmploymentEnum,
    JobPostingResponseDTO,
    RejectPostingCreateSchema,
    RejectPostingResponseDTO,
    RejectPostingSchema,
    StatusEnum,
    UserSchema,
)
from app.domain.admin.services.job_posting_services import (
    create_reject_posting_by_id_service,
    delete_job_posting_by_id_service,
    get_all_job_postings_service,
    get_job_posting_by_id_service,
    patch_job_posting_by_id_service,
)
from app.exceptions.base_exceptions import CustomException


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.get_all_job_postings_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_get_all_job_postings_service(
    mock_check_superuser, mock_get_all_job_postings_query
):
    # given
    dummy_user = AsyncMock()
    dummy_search_type = "title"
    dummy_search_keyword = "백엔드"
    dummy_status = "모집중"

    mock_data = [
        JobPostingResponseDTO(
            id=1,
            user=UserSchema(id=1),
            title="백엔드 개발자 모집",
            company="테스트 회사",
            location="서울특별시 강남구",
            employment_type=EmploymentEnum.Public,
            position="주니어 백엔드 개발자",
            history="신입 가능",
            recruitment_count=2,
            education="무관",
            deadline="2025-05-31",
            salary="5000만원",
            summary="함께 성장할 백엔드 개발자를 찾습니다.",
            description="FastAPI 및 PostgreSQL 사용 가능한 분 우대.",
            status=StatusEnum.Open,
            view_count=123,
            report=0,
            reject_postings=[
                RejectPostingSchema(id=1, user=UserSchema(id=1), content="컨텐트")
            ],
        )
    ]
    mock_check_superuser.return_value = True
    mock_get_all_job_postings_query.return_value = mock_data

    # when
    result = await get_all_job_postings_service(
        dummy_user, dummy_search_type, dummy_search_keyword, dummy_status
    )

    # then
    assert result == mock_data


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.check_existing",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.get_job_posting_by_id_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_get_job_posting_by_id_service(
    mock_check_superuser,
    mock_get_job_posting_by_id_query,
    mock_check_existing,
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_search_type = AsyncMock()

    mock_data = JobPostingResponseDTO(
        id=1,
        user=UserSchema(id=1),
        title="백엔드 개발자 모집",
        company="테스트 회사",
        location="서울특별시 강남구",
        employment_type=EmploymentEnum.Public,
        position="주니어 백엔드 개발자",
        history="신입 가능",
        recruitment_count=2,
        education="무관",
        deadline="2025-05-31",
        salary="5000만원",
        summary="함께 성장할 백엔드 개발자를 찾습니다.",
        description="FastAPI 및 PostgreSQL 사용 가능한 분 우대.",
        status=StatusEnum.Open,
        view_count=123,
        report=0,
        reject_postings=[
            RejectPostingSchema(id=1, user=UserSchema(id=1), content="컨텐트")
        ],
    )
    mock_check_existing.return_value = None
    mock_check_superuser.return_value = None
    mock_get_job_posting_by_id_query.return_value = mock_data

    # when
    result = await get_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert result == mock_data
    mock_get_job_posting_by_id_query.assert_called_once_with(dummy_id)
    mock_check_superuser.assert_called_once_with(dummy_user)


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.patch_job_posting_by_id",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_existing",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.get_job_posting_by_id_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_patch_job_posting_by_id_service(
    mock_check_superuser,
    mock_get_job_posting_by_id_query,
    mock_check_existing,
    mock_patch_job_posting_by_id,
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_data = AsyncMock()

    mock_data = JobPostingResponseDTO(
        id=1,
        user=UserSchema(id=1),
        title="백엔드 개발자 모집",
        company="테스트 회사",
        location="서울특별시 강남구",
        employment_type=EmploymentEnum.Public,
        position="주니어 백엔드 개발자",
        history="신입 가능",
        recruitment_count=2,
        education="무관",
        deadline="2025-05-31",
        salary="5000만원",
        summary="함께 성장할 백엔드 개발자를 찾습니다.",
        description="FastAPI 및 PostgreSQL 사용 가능한 분 우대.",
        status=StatusEnum.Open,
        view_count=123,
        report=0,
        reject_postings=[
            RejectPostingSchema(id=1, user=UserSchema(id=1), content="컨텐트")
        ],
    )

    mock_check_existing.return_value = None
    mock_check_superuser.return_value = None
    mock_patch_job_posting_by_id.return_value = mock_data
    mock_get_job_posting_by_id_query.return_value = dummy_data

    # when
    result = await patch_job_posting_by_id_service(dummy_id, dummy_data, dummy_user)

    # then
    assert result == mock_data
    mock_check_superuser.assert_called_once_with(dummy_user)
    mock_get_job_posting_by_id_query.assert_called_once_with(dummy_id)


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.delete_job_posting_by_id",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_existing",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.get_job_posting_by_id_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_delete_job_posting_by_id_service(
    mock_check_superuser,
    mock_get_job_posting_by_id_query,
    mock_check_existing,
    mock_delete_job_posting_by_id,
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_data = AsyncMock()

    mock_check_existing.return_value = None
    mock_check_superuser.return_value = None
    mock_delete_job_posting_by_id.return_value = None
    mock_get_job_posting_by_id_query.return_value = dummy_data

    # when
    result = await delete_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert result is None
    mock_check_superuser.assert_called_once_with(dummy_user)
    mock_get_job_posting_by_id_query.assert_called_once_with(dummy_id)


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.create_reject_posting_by_id",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_existing",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.get_job_posting_by_id_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_create_reject_posting_by_id_service_success(
    mock_check_superuser, mock_get_posting, mock_check_existing, mock_create_reject
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_posting = AsyncMock()
    dummy_request = RejectPostingCreateSchema(content="부적합")

    expected_response = RejectPostingResponseDTO(
        id=1,
        user=UserSchema(id=1),
        job_posting=JobPostingResponseDTO(
            id=1,
            user=UserSchema(id=1),
            title="백엔드 개발자 모집",
            company="테스트 회사",
            location="서울특별시 강남구",
            employment_type=EmploymentEnum.Public,
            position="주니어 백엔드 개발자",
            history="신입 가능",
            recruitment_count=2,
            education="무관",
            deadline="2025-05-31",
            salary="5000만원",
            summary="함께 성장할 백엔드 개발자를 찾습니다.",
            description="FastAPI 및 PostgreSQL 사용 가능한 분 우대.",
            status=StatusEnum.Open,
            view_count=123,
            report=0,
            reject_postings=[],
        ),
        content="부적합",
    )

    mock_check_superuser.return_value = None
    mock_get_posting.return_value = expected_response.job_posting
    mock_check_existing.return_value = None
    mock_create_reject.return_value = expected_response

    # when
    result = await create_reject_posting_by_id_service(
        dummy_id, dummy_user, dummy_request
    )

    # then
    assert result == expected_response
    mock_check_superuser.assert_called_once_with(dummy_user)
    mock_get_posting.assert_called_once_with(dummy_id)
    mock_create_reject.assert_called_once_with(
        dummy_request, expected_response.job_posting, dummy_user
    )
