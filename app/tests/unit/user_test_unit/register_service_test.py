from unittest.mock import AsyncMock, patch

import pytest
from passlib.hash import bcrypt

from app.domain.user.services.auth_services import verify_user_password
from app.domain.user.user_schema import VerifyPasswordRequest
from app.main import CustomException


@pytest.mark.asyncio
async def test_verify_password_success():
    request = VerifyPasswordRequest(password="correct_password")

    mock_user = AsyncMock()
    mock_user.password = bcrypt.hash("correct_password")

    with patch(
        "app.domain.user.services.auth_services.bcrypt.verify", return_value=True
    ):
        #  request.current_password만 꺼내서 넘김
        result = await verify_user_password(mock_user, request.password)

    # 예외 없으면 정상
    assert result is None


@pytest.mark.asyncio
async def test_verify_password_fail():
    request = VerifyPasswordRequest(password="wrong_password")

    mock_user = AsyncMock()
    mock_user.password = bcrypt.hash("correct_password")

    with patch(
        "app.domain.user.services.auth_services.bcrypt.verify", return_value=False
    ):
        with pytest.raises(CustomException) as e:
            await verify_user_password(mock_user, request.password)

    assert e.value.code == "invalid_password"
    assert e.value.status_code == 400
