from unittest.mock import AsyncMock, patch

import pytest

from app.domain.chatbot.schemas import ChatBotResponseDTO
from app.domain.chatbot.services import (
    create_chatbot_by_id_service,
    delete_chatbot_by_id_service,
    get_all_chatbots_service,
    patch_chatbot_by_id_service,
)
from app.exceptions.base_exceptions import CustomException


@pytest.mark.asyncio
@patch("app.domain.chatbot.services.check_superuser", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.get_all_chatbots", new_callable=AsyncMock)
async def test_get_chatbots_service(mock_get_queries, mock_check_superuser):
    # given
    dummy_user = object()
    mock_data = [
        ChatBotResponseDTO(id=1, step=1, is_terminate=True, selection_path="기업")
    ]

    mock_get_queries.return_value = mock_data
    mock_check_superuser.return_value = None

    # when
    result = await get_all_chatbots_service(dummy_user)

    # then

    assert result == mock_data
    mock_check_superuser.assert_called_once_with(dummy_user)


@pytest.mark.asyncio
async def test_get_chatbots_service_not_superuser():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False

    # when
    with pytest.raises(CustomException) as e:
        await get_all_chatbots_service(dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.chatbot.services.check_superuser", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.create_chatbot", new_callable=AsyncMock)
async def test_create_chatbot_by_id_service(mock_create_chatbot, mock_check_superuser):
    # given
    dummy_user = object()
    mock_create_data = AsyncMock()
    mock_data = ChatBotResponseDTO(id=1, step=1, is_terminate=True, selection_path="기업")

    mock_create_chatbot.return_value = mock_data
    mock_check_superuser.return_value = None

    # when
    result = await create_chatbot_by_id_service(dummy_user, mock_create_data)

    # then
    assert result == mock_data
    mock_check_superuser.assert_called_once_with(dummy_user)


@pytest.mark.asyncio
async def test_create_chatbot_by_id_service_not_superuser():
    # given
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    mock_data = AsyncMock()

    # when
    with pytest.raises(CustomException) as e:
        await create_chatbot_by_id_service(dummy_user, mock_data)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
async def test_patch_chatbot_by_id_service_not_superuser():
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False
    dummy_data = AsyncMock()

    # when
    with pytest.raises(CustomException) as e:
        await patch_chatbot_by_id_service(dummy_id, dummy_user, dummy_data)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.chatbot.services.check_superuser", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.get_chatbot_by_id", new_callable=AsyncMock)
async def test_patch_chatbot_by_id_service_not_found(
    get_chatbot_by_id, mock_check_superuser
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_data = AsyncMock()

    mock_check_superuser.return_value = None
    get_chatbot_by_id.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await patch_chatbot_by_id_service(dummy_id, dummy_user, dummy_data)

    # then
    assert e.value.code == "chatbot_not_found"


@pytest.mark.asyncio
@patch("app.domain.chatbot.services.get_chatbot_by_id", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.check_superuser", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.patch_chatbot_by_id", new_callable=AsyncMock)
async def test_patch_chatbot_by_id_service(
    mock_patch, mock_check_existing, mock_check_superuser, mock_get_chatbot
):
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_data = AsyncMock()

    mock_patch_data = ChatBotResponseDTO(
        id=1, step=1, is_terminate=True, selection_path="updated_기업"
    )
    mock_get_chatbot.return_value = dummy_data
    mock_check_existing.return_value = dummy_data
    mock_check_superuser.return_value = None
    mock_patch.return_value = mock_patch_data

    # when
    result = await patch_chatbot_by_id_service(dummy_id, dummy_user, dummy_data)

    # then
    assert result == mock_patch_data
    mock_check_superuser.assert_called_once_with(dummy_user)
    mock_get_chatbot.assert_called_once_with(dummy_id)


@pytest.mark.asyncio
async def test_delete_chatbot_by_id_service_not_superuser():
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_user.is_superuser = False

    # when
    with pytest.raises(CustomException) as e:
        await delete_chatbot_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "permission_denied"


@pytest.mark.asyncio
@patch("app.domain.chatbot.services.check_superuser", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.get_chatbot_by_id", new_callable=AsyncMock)
async def test_delete_chatbot_by_id_service_not_found(
    get_chatbot_by_id, mock_check_superuser
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()

    mock_check_superuser.return_value = None
    get_chatbot_by_id.return_value = None

    # when
    with pytest.raises(CustomException) as e:
        await delete_chatbot_by_id_service(dummy_id, dummy_user)

    # then
    assert e.value.code == "chatbot_not_found"


@pytest.mark.asyncio
@patch("app.domain.chatbot.services.get_chatbot_by_id", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.check_superuser", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.check_existing", new_callable=AsyncMock)
@patch("app.domain.chatbot.services.delete_chatbot_by_id", new_callable=AsyncMock)
async def test_delete_chatbot_by_id_service_not_found(
    mock_delete_by_id, mock_check_existing, mock_check_superuser, mock_get_chatbot
):
    # given
    dummy_id = 1
    dummy_user = AsyncMock()
    dummy_data = AsyncMock()

    mock_delete_by_id.return_value = None
    mock_check_existing.return_value = None
    mock_check_superuser.return_value = None
    mock_get_chatbot.return_value = dummy_data

    # when
    result = await delete_chatbot_by_id_service(dummy_id, dummy_user)

    # then
    assert result is None
    mock_get_chatbot.assert_called_once_with(dummy_id)
    mock_check_superuser.assert_called_once_with(dummy_user)
