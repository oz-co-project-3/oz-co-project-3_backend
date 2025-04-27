from unittest.mock import AsyncMock, patch

import pytest

from app.domain.admin.schemas.resume_schemas import (
    ResumeResponseDTO,
    StatusEnum,
    UserSchema,
    WorkExpResponseDTO,
)
from app.domain.admin.services.resume_services import (
    delete_resume_by_id_service,
    get_all_resumes_service,
    get_resume_by_id_service,
)
from app.exceptions.base_exceptions import CustomException


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.resume_services.get_resumes_by_name",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.resume_services.check_superuser", new_callable=AsyncMock
)
async def test_get_all_resumes_service_with_name(
    mock_check_superuser, mock_get_resumes_by_name
):
    # given
    dummy_user = AsyncMock()
    dummy_name = AsyncMock()

    mock_data = [
        ResumeResponseDTO(
            id=1,
            user=UserSchema(id=1),
            title="test",
            visibility=True,
            name="이름",
            phone_number="01000000000",
            email="test@test.com",
            interests="test",
            desired_area="서울",
            education="학력",
            school_name="학교",
            graduation_status="ㅈ졸업",
            introduce="소개",
            status=StatusEnum.Writing,
            work_experiences=[
                WorkExpResponseDTO(id=1, company="회사", period="기간", position="포지션")
            ],
        )
    ]

    mock_check_superuser.return_value = None
    mock_get_resumes_by_name.return_value = mock_data

    # when
    result = await get_all_resumes_service(dummy_user, dummy_name)

    # then
    assert result == mock_data
    mock_check_superuser.called_once_with(dummy_user)


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.resume_services.get_all_resumes_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.resume_services.check_superuser", new_callable=AsyncMock
)
async def test_get_all_resumes_service(
    mock_check_superuser, mock_get_all_resumes_query
):
    # given
    dummy_user = AsyncMock()
    dummy_name = None

    mock_data = [
        ResumeResponseDTO(
            id=1,
            user=UserSchema(id=1),
            title="test",
            visibility=True,
            name="이름",
            phone_number="01000000000",
            email="test@test.com",
            interests="test",
            desired_area="서울",
            education="학력",
            school_name="학교",
            graduation_status="ㅈ졸업",
            introduce="소개",
            status=StatusEnum.Writing,
            work_experiences=[
                WorkExpResponseDTO(id=1, company="회사", period="기간", position="포지션")
            ],
        )
    ]

    mock_check_superuser.return_value = None
    mock_get_all_resumes_query.return_value = mock_data

    # when
    result = await get_all_resumes_service(dummy_user, dummy_name)

    # then
    assert result == mock_data
    mock_check_superuser.called_once_with(dummy_user)


@pytest.mark.asyncio
async def test_get_all_resumes_service_not_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_name = AsyncMock()

    # when
    with pytest.raises(CustomException) as e:
        await get_all_resumes_service(dummy_user, dummy_name)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.resume_services.get_resume_by_id", new_callable=AsyncMock
)
@patch(
    "app.domain.admin.services.resume_services.check_superuser", new_callable=AsyncMock
)
@patch(
    "app.domain.admin.services.resume_services.check_existing", new_callable=AsyncMock
)
async def test_get_resume_by_id_service(
    mock_check_superuser, mock_check_existing, mock_get_resume_by_id
):
    # given
    dummy_user = AsyncMock()
    dummy_id = 1

    mock_data = ResumeResponseDTO(
        id=1,
        user=UserSchema(id=1),
        title="test",
        visibility=True,
        name="이름",
        phone_number="01000000000",
        email="test@test.com",
        interests="test",
        desired_area="서울",
        education="학력",
        school_name="학교",
        graduation_status="ㅈ졸업",
        introduce="소개",
        status=StatusEnum.Writing,
        work_experiences=[
            WorkExpResponseDTO(id=1, company="회사", period="기간", position="포지션")
        ],
    )

    mock_check_superuser.return_value = None
    mock_get_resume_by_id.return_value = mock_data
    mock_check_existing.return_value = None

    # when
    result = await get_resume_by_id_service(dummy_user, dummy_id)

    # then
    assert result == mock_data
    mock_check_superuser.called_once_with(dummy_user)


@pytest.mark.asyncio
async def test_get_resume_by_id_service_not_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_id = 1

    # when
    with pytest.raises(CustomException) as e:
        await get_resume_by_id_service(dummy_user, dummy_id)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.admin.services.resume_services.check_superuser")
@patch("app.domain.admin.services.resume_services.get_resume_by_id")
async def test_get_resume_by_id_service_not_found(
    mock_get_resume_by_id, mock_check_superuser
):
    dummy_user = AsyncMock()
    dummy_id = 1

    mock_get_resume_by_id.return_value = None
    mock_check_superuser.return_value = None

    with pytest.raises(CustomException) as e:
        await get_resume_by_id_service(dummy_user, dummy_id)

    assert e.value.code == "resume_not_found"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.resume_services.get_resume_by_id", new_callable=AsyncMock
)
@patch(
    "app.domain.admin.services.resume_services.delete_resume_by_id",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.resume_services.check_superuser", new_callable=AsyncMock
)
@patch(
    "app.domain.admin.services.resume_services.check_existing", new_callable=AsyncMock
)
async def test_delete_resume_by_id_service(
    mock_check_superuser,
    mock_check_existing,
    mock_delete_resume_by_id,
    mock_get_resume_by_id,
):
    # given
    dummy_user = AsyncMock()
    dummy_data = AsyncMock()
    dummy_id = 1

    mock_check_superuser.return_value = None
    mock_get_resume_by_id.return_value = dummy_data
    mock_check_existing.return_value = None
    mock_delete_resume_by_id.return_value = None

    # when
    result = await delete_resume_by_id_service(dummy_user, dummy_id)

    # then
    assert result is None
    mock_check_superuser.called_once_with(dummy_user)
    mock_get_resume_by_id.called_once_with(dummy_id)


@pytest.mark.asyncio
async def test_delete_resume_by_id_service_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_id = 1

    # when
    with pytest.raises(CustomException) as e:
        await delete_resume_by_id_service(dummy_user, dummy_id)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.admin.services.resume_services.check_superuser")
@patch("app.domain.admin.services.resume_services.get_resume_by_id")
async def test_delete_resume_by_id_service_not_found(
    mock_get_resume_by_id, mock_check_superuser
):
    dummy_user = AsyncMock()
    dummy_id = 1

    mock_get_resume_by_id.return_value = None
    mock_check_superuser.return_value = None

    with pytest.raises(CustomException) as e:
        await delete_resume_by_id_service(dummy_user, dummy_id)

    assert e.value.code == "resume_not_found"
