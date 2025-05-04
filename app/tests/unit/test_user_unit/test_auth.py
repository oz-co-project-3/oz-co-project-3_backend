# from unittest.mock import AsyncMock, patch
#
# import pytest
#
# from app.api.v1.user import EmailVerifyRequest
# from app.domain.user.models import UserStatus
# from app.domain.user.schema import LoginRequest
# from app.domain.user.services.auth_services import login_user, logout_user
#
#
# from app.main import CustomException
#
# """
# [로그인 유닛 테스트]
# 1. 로그인 성공
# 2. 로그인 실패 - 비밀번호 틀림
# 3. 로그인 실패 - 유저 없음
# """
#
#
# @pytest.mark.asyncio
# async def test_login_user_success_unit():
#     request = LoginRequest(email="user@example.com", password="1234!1234!")
#
#     mock_user = AsyncMock()
#     mock_user.id = 1
#     mock_user.email = "user@example.com"
#     mock_user.user_type = "seeker"
#     mock_user.status = "active"
#     mock_user.email_verified = True
#     mock_user.password = "hashed"
#
#     # 로그인 시 seeker 유저 정보도 가져오므로 SeekerUser.get도 mock 해야 함
#     mock_seeker = AsyncMock()
#     mock_seeker.name = "테스트유저"
#
#     with (
#         patch(
#             "app.domain.user.services.auth_services.BaseUser.get_or_none",
#             new=AsyncMock(return_value=mock_user),
#         ),
#         patch(
#             "app.domain.user.services.auth_services.SeekerUser.get",
#             new=AsyncMock(return_value=mock_seeker),
#         ),
#         patch(
#             "app.domain.user.services.auth_services.bcrypt.verify", return_value=True
#         ),
#         patch(
#             "app.domain.user.services.auth_services.create_jwt_tokens",
#             return_value=("access", "refresh"),
#         ),
#         patch("app.domain.user.services.auth_services.redis.set", new=AsyncMock()),
#     ):
#         response = await login_user(request)
#
#     assert response.data.email == "user@example.com"
#     assert response.data.access_token == "access"
#     assert response.data.name == "테스트유저"
#
#
# @pytest.mark.asyncio
# async def test_login_fail_wrong_password_unit():
#     request = LoginRequest(email="user@example.com", password="wrongpass")
#
#     mock_user = AsyncMock()
#     mock_user.email_verified = True
#     mock_user.status = UserStatus.ACTIVE
#     mock_user.password = "hashed"
#
#     with patch(
#         "app.domain.user.services.auth_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=mock_user),
#     ), patch(
#         "app.domain.user.services.auth_services.bcrypt.verify", return_value=False
#     ):
#         with pytest.raises(CustomException) as e:
#             await login_user(request)
#
#         assert e.value.code == "invalid_credentials"
#         assert e.value.status_code == 401
#
#
# @pytest.mark.asyncio
# async def test_login_fail_user_not_exist_unit():
#     request = LoginRequest(email="no_user@example.com", password="1234!1234!")
#
#     with patch(
#         "app.domain.user.services.auth_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=None),
#     ):
#         with pytest.raises(CustomException) as e:
#             await login_user(request)
#
#         assert e.value.code == "invalid_credentials"
#         assert e.value.status_code == 401
#
#
# """
# [로그아웃 유닛 테스트]
# 4. 로그아웃 성공
# 5. 로그아웃 실패 - 토큰 삭제 실패 (access_token)
# """
#
#
# @pytest.mark.asyncio
# async def test_logout_user_success_unit():
#     mock_user = AsyncMock()
#     mock_user.id = 1
#
#     # redis.delete가 두 번 호출될 때 모두 1 반환 → 삭제 성공
#     async_mock = AsyncMock()
#     async_mock.side_effect = [1, 1]  # access, refresh 모두 삭제 성공
#
#     with patch("app.domain.user.services.auth_services.redis.delete", async_mock):
#         result = await logout_user(mock_user)
#
#     assert result["message"] == "로그아웃이 완료되었습니다."
#     assert async_mock.call_count == 2
#
#
# # 토큰 없는 로그아웃
# @pytest.mark.asyncio
# async def test_logout_user_token_invalid_unit():
#     mock_user = AsyncMock()
#     mock_user.id = 1
#
#     # Redis 토큰 삭제 실패 → 예외 발생
#     mock_delete = AsyncMock()
#     mock_delete.side_effect = [0, 1]  # access 삭제 실패
#
#     with patch("app.domain.user.services.auth_services.redis.delete", mock_delete):
#         with pytest.raises(CustomException) as e:
#             await logout_user(mock_user)
#
#         assert e.value.code == "invalid_token"
#         assert e.value.status_code == 401
#
#
# """
# [이메일 관련 유닛 테스트]
# 6. 이메일 인증코드 검증
# 7. 이메일 중복확인 (사용 중인 이메일)
# 8. 이메일 중복확인 (사용 가능한 이메일)
# 9. 이메일 인증코드 재전송 성공
# 10. 이메일 인증코드 재전송 실패 - 유저 없음
# """
#
#
# @pytest.mark.asyncio
# async def test_verify_email_code_no_dependency():
#     # 요청 객체 준비
#     request = EmailVerifyRequest(
#         email="test_verify@example.com", verification_code="123456"
#     )
#
#     # Mock 유저 생성
#     mock_user = AsyncMock()
#     mock_user.email_verified = False
#     mock_user.status = "pending"
#     mock_user.email = "test_verify@example.com"
#     mock_user.save = AsyncMock()
#
#     with patch(
#         "app.domain.user.services.email_services.redis.get",
#         new=AsyncMock(return_value="123456"),
#     ), patch(
#         "app.domain.user.services.email_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=mock_user),
#     ):
#         result = await verify_email_code(request)
#
#     # 검증
#     assert result["data"]["email"] == "test_verify@example.com"
#     assert result["data"]["email_verified"] is True
#
#
# @pytest.mark.asyncio
# async def test_check_email_duplicate_used_email():
#     # 이메일이 이미 존재하는 경우
#     with patch(
#         "app.domain.user.services.user_register_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=AsyncMock()),
#     ):
#         result = await check_email_duplicate("used@example.com")
#         assert result.is_available is False
#         assert result.message == "이미 사용 중인 이메일입니다."
#
#
# @pytest.mark.asyncio
# async def test_check_email_duplicate_available_email():
#     # 이메일이 사용 가능할 경우
#     with patch(
#         "app.domain.user.services.user_register_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=None),
#     ):
#         result = await check_email_duplicate("new@example.com")
#         assert result.is_available is True
#         assert result.message == "사용 가능한 이메일입니다."
#
#
# @pytest.mark.asyncio
# async def test_resend_verification_email_success():
#     # 요청
#     request = ResendEmailRequest(email="test@example.com")
#
#     # 유저 mock
#     mock_user = AsyncMock()
#     mock_user.email_verified = False
#     mock_user.email = "test@example.com"
#
#     with patch(
#         "app.domain.user.services.email_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=mock_user),
#     ), patch(
#         "app.domain.user.services.email_services.send_email_code",
#         new=AsyncMock(return_value="123456"),
#     ):
#         result = await resend_verification_email(request)
#
#     assert result["message"] == "인증코드가 재전송되었습니다."
#     assert result["data"]["email"] == "test@example.com"
#
#
# @pytest.mark.asyncio
# async def test_resend_verification_email_user_not_found():
#     request = ResendEmailRequest(email="notfound@example.com")
#
#     with patch(
#         "app.domain.user.services.email_services.BaseUser.get_or_none",
#         new=AsyncMock(return_value=None),
#     ):
#         with pytest.raises(CustomException) as e:
#             await resend_verification_email(request)
#
#         assert e.value.code == "user_not_found"
#         assert e.value.status_code == 404
