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
    dummy_search_type = AsyncMock()
    dummy_search_keyword = AsyncMock()
    dummy_status = AsyncMock()

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
    mock_check_superuser.assert_called_once_with(dummy_user)


@pytest.mark.asyncio
async def test_get_all_job_postings_service_not_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_search_type = AsyncMock()
    dummy_search_keyword = AsyncMock()
    dummy_status = AsyncMock()

    # when
    with pytest.raises(CustomException) as e:
        await get_all_job_postings_service(
            dummy_user, dummy_search_type, dummy_search_keyword, dummy_status
        )

    # then
    assert e.value.code == "permission_denied"


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
    mock_check_existing.assert_called_once_with(
        mock_data, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found"
    )
    mock_check_superuser.assert_called_once_with(dummy_user)


@pytest.mark.asyncio
async def test_get_job_posting_by_id_service_not_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_id = 1

    # when
    with pytest.raises(CustomException) as e:
        await get_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_get_job_posting_by_id_service_not_found(mock_check_superuser):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()

    mock_check_superuser.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await get_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "job_posting_not_found"


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
    mock_check_existing.assert_called_once_with(
        dummy_data, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found"
    )


@pytest.mark.asyncio
async def test_patch_job_posting_by_id_service_not_permitted():
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_data = AsyncMock()

    # when
    with pytest.raises(CustomException) as e:
        await patch_job_posting_by_id_service(dummy_id, dummy_data, dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_patch_job_posting_by_id_service_not_found(mock_check_superuser):
    # given
    dummy_id = 1
    dummy_data = AsyncMock()
    dummy_user = AsyncMock()

    mock_check_superuser.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await patch_job_posting_by_id_service(dummy_id, dummy_data, dummy_user)

    # then
    assert e.value.code == "job_posting_not_found"


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
    mock_check_existing.assert_called_once_with(
        dummy_data, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found"
    )


@pytest.mark.asyncio
async def test_delete_job_posting_by_id_service_not_permitted():
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False

    # when
    with pytest.raises(CustomException) as e:
        await delete_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
async def test_delete_job_posting_by_id_service_not_found(mock_check_superuser):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()

    mock_check_superuser.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "job_posting_not_found"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.get_job_posting_by_id_query",
    new_callable=AsyncMock,
)
async def test_delete_job_posting_by_id_service_not_found(
    mock_get_job_posting_by_id_query, mock_check_superuser
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()

    mock_check_superuser.return_value = None
    mock_get_job_posting_by_id_query.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_job_posting_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "job_posting_not_found"


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
    mock_check_existing.assert_called_once_with(
        expected_response.job_posting, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found"
    )
    mock_create_reject.assert_called_once_with(
        dummy_request, expected_response.job_posting, dummy_user
    )


@pytest.mark.asyncio
async def test_create_reject_posting_by_id_service_permission_denied():
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_request = RejectPostingCreateSchema(content="부적합")

    # when
    with pytest.raises(CustomException) as e:
        await create_reject_posting_by_id_service(dummy_id, dummy_user, dummy_request)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.job_posting_services.check_superuser",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.job_posting_services.get_job_posting_by_id_query",
    new_callable=AsyncMock,
)
async def test_create_reject_posting_by_id_service_not_found(
    mock_get_posting, mock_check_superuser
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_request = RejectPostingCreateSchema(content="부적합")

    mock_check_superuser.return_value = None
    mock_get_posting.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await create_reject_posting_by_id_service(dummy_id, dummy_user, dummy_request)

    # then
    assert e.value.code == "job_posting_not_found"
