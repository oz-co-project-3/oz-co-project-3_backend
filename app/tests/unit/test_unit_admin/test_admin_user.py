from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.admin.schemas.user_schemas import (
    CorpUserResponseSchema,
    SeekerUserResponseSchema,
    UserResponseDTO,
    UserUnionResponseDTO,
)
from app.domain.admin.services.user_services import (
    get_user_all_service,
    get_user_by_id_service,
)
from app.domain.services.verification import CustomException


@pytest.mark.asyncio
@patch("app.domain.admin.services.user_services.get_corp_users", new_callable=AsyncMock)
@patch(
    "app.domain.admin.services.user_services.get_seeker_users", new_callable=AsyncMock
)
@patch(
    "app.domain.admin.services.user_services.check_superuser", new_callable=AsyncMock
)
async def test_get_user_all_service(
    mock_check_superuser, mock_get_seeker_users, mock_get_corp_users
):
    # given
    dummy_user = AsyncMock()
    search = "test"

    seeker_user = MagicMock()
    seeker_user.user = MagicMock(
        id=1,
        email="test@test.com",
        user_type="seeker",
        status="active",
        email_verified=True,
        is_superuser=False,
        created_at=datetime.now(),
        deleted_at=None,
        gender="male",
    )
    seeker_user.id = 1
    seeker_user.name = "홍길동"
    seeker_user.phone_number = "01012345678"
    seeker_user.birth = date(1990, 1, 1)
    seeker_user.interests = "AI"
    seeker_user.purposes = "학습"
    seeker_user.sources = "지인 추천"
    seeker_user.applied_posting = None
    seeker_user.applied_posting_count = 3
    seeker_user.is_social = False
    seeker_user.status = "active"

    corp_user = MagicMock()
    corp_user.user = MagicMock(
        id=2,
        email="corp@test.com",
        user_type="corp",
        status="active",
        email_verified=True,
        is_superuser=False,
        created_at=datetime.now(),
        deleted_at=None,
        gender="female",
    )
    corp_user.id = 2
    corp_user.company_name = "테스트 회사"
    corp_user.business_start_date = datetime.now()
    corp_user.business_number = "123-45-67890"
    corp_user.company_description = "테스트 회사입니다."
    corp_user.manager_name = "김매니저"
    corp_user.manager_phone_number = "01098765432"
    corp_user.manager_email = "manager@test.com"
    corp_user.gender = "female"

    mock_get_seeker_users.return_value = [seeker_user]
    mock_get_corp_users.return_value = [corp_user]
    mock_check_superuser.return_value = None

    # when
    result = await get_user_all_service(
        dummy_user, seeker=True, corp=True, search=search
    )

    # then
    assert len(result) == 2
    assert isinstance(result[0], UserUnionResponseDTO)
    assert result[0].seeker is not None or result[1].corp is not None


@pytest.mark.asyncio
async def test_get_user_all_service_not_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_search = AsyncMock()

    # when
    with pytest.raises(CustomException) as e:
        await get_user_all_service(
            dummy_user, seeker=True, corp=True, search=dummy_search
        )

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.user_services.get_corp_user_by_user_id",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.user_services.get_seeker_user_by_user_id",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.user_services.get_user_by_id_query",
    new_callable=AsyncMock,
)
@patch("app.domain.admin.services.user_services.check_existing", new_callable=AsyncMock)
@patch(
    "app.domain.admin.services.user_services.check_superuser", new_callable=AsyncMock
)
async def test_get_user_by_id_service(
    mock_check_superuser,
    mock_check_existing,
    mock_get_user,
    mock_get_seeker,
    mock_get_corp,
):
    dummy_user = AsyncMock()
    dummy_id = 1

    base_user = SimpleNamespace(
        id=1,
        email="test@test.com",
        user_type="seeker",
        status="active",
        email_verified=True,
        is_superuser=False,
        created_at=datetime.now(),
        deleted_at=None,
        gender="male",
    )

    seeker_user = SimpleNamespace(
        id=1,
        name="홍길동",
        phone_number="01012345678",
        birth=date(1990, 1, 1),
        interests="AI",
        purposes="학습",
        sources="지인 추천",
        applied_posting=None,
        applied_posting_count=3,
        is_social=False,
        status="active",
        user=base_user,
    )

    corp_user = SimpleNamespace(
        id=2,
        company_name="테스트 회사",
        business_start_date=datetime.now(),
        business_number="123-45-67890",
        company_description="설명",
        manager_name="홍매니저",
        manager_phone_number="01012345678",
        manager_email="manager@test.com",
        gender="female",
        user=base_user,
    )

    mock_check_superuser.return_value = None
    mock_check_existing.return_value = None
    mock_get_user.return_value = base_user
    mock_get_seeker.return_value = seeker_user
    mock_get_corp.return_value = corp_user

    result = await get_user_by_id_service(dummy_user, dummy_id)

    assert isinstance(result, UserUnionResponseDTO)
    assert result.base.email == base_user.email
    assert result.seeker.name == seeker_user.name
    assert result.corp.company_name == corp_user.company_name


@pytest.mark.asyncio
async def test_get_user_by_id_service_not_permitted():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_id = 1

    # when
    with pytest.raises(CustomException) as e:
        await get_user_by_id_service(dummy_user, dummy_id)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch(
    "app.domain.admin.services.user_services.get_user_by_id_query",
    new_callable=AsyncMock,
)
@patch(
    "app.domain.admin.services.user_services.check_superuser", new_callable=AsyncMock
)
async def test_get_user_by_id_service_not_found(mock_check_superuser, mock_get_user):
    # given
    dummy_user = AsyncMock()
    dummy_id = 1

    mock_check_superuser.return_value = None
    mock_get_user.return_value = None
    # when
    with pytest.raises(CustomException) as e:
        await get_user_by_id_service(dummy_user, dummy_id)
    # then
    assert e.value.code == "user_not_found"
