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

    mock_check_author.assert_called_once_with(dummy_comment, dummy_user)
    mock_patch_comment.assert_called_once_with(dummy_comment, dummy_comment)


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
    mock_check_author.assert_called_once_with(dummy_comment, dummy_user)
