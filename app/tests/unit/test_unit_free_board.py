from unittest.mock import AsyncMock, patch

import pytest

from app.domain.free_board.schemas import FreeBoardResponseDTO, UserSchema
from app.domain.free_board.services import (
    create_free_board_by_id_service,
    delete_free_board_by_id_service,
    get_all_free_board_service,
    get_free_board_by_id_service,
    patch_free_board_by_id_service,
)
from app.domain.services.verification import CustomException


@pytest.mark.asyncio
@patch("app.domain.free_board.services.create_free_board_by_id", new_callable=AsyncMock)
async def test_create_free_board_by_id_service(mock_create):
    # given
    dummy_user = object()
    dummy_data = AsyncMock()
    dummy_result = FreeBoardResponseDTO(
        id=1,
        user=UserSchema(id=1),
        title="test title",
        content="test content",
        image_url=None,
        view_count=1,
        created_at="2025-04-23T12:00:00",
        updated_at="2025-04-23T12:00:00",
    )
    mock_create.return_value = dummy_result

    # when
    result = await create_free_board_by_id_service(dummy_data, dummy_user)

    # then
    mock_create.assert_called_once_with(dummy_data, dummy_user)
    assert result == dummy_result


@pytest.mark.asyncio
@patch("app.domain.free_board.services.get_free_boards_query", new_callable=AsyncMock)
async def test_get_all_free_board_service(mock_get_query):
    # 가짜 반환값 설정
    mock_data = [
        FreeBoardResponseDTO(
            id=1,
            user=UserSchema(id=1),
            title="test title",
            content="test content",
            image_url=None,
            view_count=1,
            created_at="2025-04-23T12:00:00",
            updated_at="2025-04-23T12:00:00",
        )
    ]
    mock_get_query.return_value = mock_data

    # 테스트 실행
    result = await get_all_free_board_service()

    # 검증
    assert result == mock_data
    mock_get_query.assert_called_once()


@pytest.mark.asyncio
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_get_free_board_by_id_service(mock_get_query):
    # given
    dummy_id = 100
    mock_data = FreeBoardResponseDTO(
        id=1,
        user=UserSchema(id=1),
        title="test title",
        content="test content",
        image_url=None,
        view_count=1,
        created_at="2025-04-23T12:00:00",
        updated_at="2025-04-23T12:00:00",
    )
    mock_get_query.return_value = mock_data

    # when
    result = await get_free_board_by_id_service(dummy_id)

    # then
    assert result == mock_data


@pytest.mark.asyncio
@patch("app.domain.free_board.services.patch_free_board_by_id", new_callable=AsyncMock)
@patch("app.domain.free_board.services.check_author", new_callable=AsyncMock)
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_patch_free_board_by_id_service(
    mock_get_query, mock_check_author, mock_patch_free_board_by_id
):
    # given
    dummy_id = 100
    dummy_user = object()
    dummy_obj = object()

    mock_get_query.return_value = dummy_obj
    mock_patch_free_board_by_id.return_value = FreeBoardResponseDTO(
        id=1,
        user=UserSchema(id=1),
        title="updated title",
        content="updated content",
        image_url=None,
        view_count=1,
        created_at="2025-04-23T12:00:00",
        updated_at="2025-04-23T12:00:00",
    )
    mock_check_author.return_value = None

    # when
    result = await patch_free_board_by_id_service(dummy_id, dummy_obj, dummy_user)

    # then
    assert result.title == "updated title"
    assert result.content == "updated content"


@pytest.mark.asyncio
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_patch_free_board_not_found(mock_get_query):
    # given
    dummy_id = 100
    dummy_user = object()
    dummy_obj = object()

    mock_get_query.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await patch_free_board_by_id_service(dummy_id, dummy_obj, dummy_user)

    # then
    assert e.value.code == "free_board_not_found"


@pytest.mark.asyncio
@patch("app.domain.free_board.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_patch_free_board_not_author(mock_get_query, mock_check_existing):
    # given

    # 현재 유저
    dummy_user = AsyncMock()
    dummy_user.id = 1
    dummy_user.is_superuser = False

    # patch 대상 객체
    dummy_obj = AsyncMock()

    # 게시글 객체
    dummy_board = AsyncMock()
    dummy_board.user_id = 2  # 작성자가 아님
    dummy_board.id = 100

    mock_get_query.return_value = dummy_board
    mock_check_existing.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await patch_free_board_by_id_service(dummy_board.id, dummy_obj, dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_delete_free_board_not_found(mock_get_query):
    # given
    dummy_id = 100
    dummy_user = object()

    mock_get_query.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_free_board_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "free_board_not_found"


@pytest.mark.asyncio
@patch("app.domain.free_board.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_delete_free_board_not_author(mock_get_query, mock_check_existing):
    # given
    # 현재 유저
    dummy_user = AsyncMock()
    dummy_user.id = 1
    dummy_user.is_superuser = False

    # 게시글 객체
    dummy_board = AsyncMock()
    dummy_board.user_id = 2  # 작성자가 아님
    dummy_board.id = 100

    mock_get_query.return_value = dummy_board
    mock_check_existing.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_free_board_by_id_service(dummy_board.id, dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.free_board.services.delete_free_board_by_id", new_callable=AsyncMock)
@patch("app.domain.free_board.services.check_author", new_callable=AsyncMock)
@patch("app.domain.free_board.services.get_free_board_query", new_callable=AsyncMock)
async def test_delete_free_board_by_id_service(
    mock_get_query,
    mock_check_author,
    mock_delete_board,
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_board = AsyncMock()

    mock_get_query.return_value = dummy_board
    mock_check_author.return_value = None
    mock_delete_board.return_value = None

    # when
    result = await delete_free_board_by_id_service(dummy_id, dummy_user)

    # then
    assert result is None
