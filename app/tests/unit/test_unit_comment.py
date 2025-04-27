from unittest.mock import AsyncMock, patch

import pytest

from app.domain.comment.schemas import CommentResponseDTO
from app.domain.comment.services import (
    create_comment_by_id_service,
    delete_comment_by_id_service,
    get_all_comments_service,
    patch_comment_by_id_service,
)
from app.exceptions.base_exceptions import CustomException


@pytest.mark.asyncio
@patch("app.domain.comment.services.create_comment_by_id", new_callable=AsyncMock)
async def test_create_comment_by_id_service(mock_create):
    # given
    dummy_id = 1
    dummy_comment = AsyncMock()
    dummy_user = object()

    mock_data = CommentResponseDTO(
        id=1,
        content="테스트 댓글",
        created_at="2025-04-23T12:00:00",
        updated_at="2025-04-23T12:00:00",
    )

    mock_create.return_value = mock_data

    # when
    result = await create_comment_by_id_service(dummy_comment, dummy_id, dummy_user)

    # then
    assert result == mock_data


@pytest.mark.asyncio
@patch("app.domain.comment.services.get_comments_query", new_callable=AsyncMock)
async def test_get_all_comments_service(mock_get_comments):
    # given
    dummy_id = 1

    mock_data = [
        CommentResponseDTO(
            id=1,
            content="테스트 댓글",
            created_at="2025-04-23T12:00:00",
            updated_at="2025-04-23T12:00:00",
        )
    ]
    mock_get_comments.return_value = mock_data

    # when
    result = await get_all_comments_service(dummy_id)

    # then
    assert result == mock_data


@pytest.mark.asyncio
@patch("app.domain.comment.services.get_comment_query", new_callable=AsyncMock)
@patch("app.domain.comment.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.comment.services.check_author", new_callable=AsyncMock)
@patch("app.domain.comment.services.patch_comment_by_id", new_callable=AsyncMock)
async def test_patch_comment_by_id_service(
    mock_patch_comment, mock_check_author, mock_check_existing, mock_get_comment
):
    # given
    dummy_id = 100
    dummy_user = object()
    dummy_comment = AsyncMock()

    mock_get_comment.return_value = dummy_comment
    mock_patch_comment.return_value = CommentResponseDTO(
        id=1,
        content="updated content",
        created_at="2025-04-23T12:00:00",
        updated_at="2025-04-23T12:00:00",
    )
    mock_check_author.return_value = None
    mock_check_existing.return_value = None
    # when
    result = await patch_comment_by_id_service(dummy_comment, dummy_id, dummy_user)

    # then
    assert result.content == "updated content"

    mock_check_existing.assert_called_once_with(  # 주어진 id로 조회된 결과
        dummy_comment, "해당 댓글을 찾을 수 없습니다.", "comment_not_found"
    )
    mock_check_author.assert_called_once_with(dummy_comment, dummy_user)
    mock_patch_comment.assert_called_once_with(dummy_comment, dummy_comment)


@pytest.mark.asyncio
@patch("app.domain.comment.services.get_comment_query", new_callable=AsyncMock)
async def test_patch_comment_by_id_service_not_found(mock_get_comment):
    # given
    dummy_data = AsyncMock()
    dummy_id = 100
    dummy_user = object()

    mock_get_comment.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await patch_comment_by_id_service(dummy_data, dummy_id, dummy_user)

    # then
    assert e.value.code == "comment_not_found"


@pytest.mark.asyncio
@patch("app.domain.comment.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.comment.services.get_comment_query", new_callable=AsyncMock)
async def test_patch_comment_by_id_service_not_author(
    mock_get_comment, mock_check_existing
):
    # given
    # 접속한 유저
    dummy_data = object()
    mock_user = AsyncMock()
    mock_user.id = 1
    mock_user.is_superuser = False

    # 코멘트 작성 유저
    mock_comment = AsyncMock()
    mock_comment.user_id = 2

    mock_get_comment.return_value = mock_comment
    mock_check_existing.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await patch_comment_by_id_service(dummy_data, mock_comment.user_id, mock_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.comment.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.comment.services.get_comment_query", new_callable=AsyncMock)
async def test_delete_comment_by_id_service_not_author(
    mock_get_comment, mock_check_existing
):
    # given
    # 접속한 유저
    dummy_data = object()
    mock_user = AsyncMock()
    mock_user.id = 1
    mock_user.is_superuser = False

    # 코멘트 작성 유저
    mock_comment = AsyncMock()
    mock_comment.user_id = 2

    mock_get_comment.return_value = mock_comment
    mock_check_existing.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_comment_by_id_service(mock_comment.user_id, mock_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.comment.services.get_comment_query", new_callable=AsyncMock)
async def test_delete_comment_by_id_service_not_found(mock_get_comment):
    # given
    dummy_id = 100
    dummy_user = object()

    mock_get_comment.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_comment_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "comment_not_found"


@pytest.mark.asyncio
@patch("app.domain.comment.services.get_comment_query", new_callable=AsyncMock)
@patch("app.domain.comment.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.comment.services.check_author", new_callable=AsyncMock)
async def test_delete_comment_by_id_service(
    mock_check_author, mock_check_existing, mock_get_comment
):
    # given
    dummy_id = 100
    dummy_user = object()
    dummy_comment = AsyncMock()

    mock_get_comment.return_value = dummy_comment
    mock_check_author.return_value = None
    mock_check_existing.return_value = None

    # when
    result = await delete_comment_by_id_service(dummy_id, dummy_user)

    # then
    assert result is None

    mock_check_existing.assert_called_once_with(  # 주어진 id로 조회된 결과
        dummy_comment, "해당 댓글을 찾을 수 없습니다.", "comment_not_found"
    )
    mock_check_author.assert_called_once_with(dummy_comment, dummy_user)
