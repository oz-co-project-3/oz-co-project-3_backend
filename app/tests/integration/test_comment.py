import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.comment.models import Comment
from app.domain.free_board.models import FreeBoard
from app.domain.user.models import BaseUser, CorporateUser, SeekerUser


@pytest.fixture(scope="module")
async def client(apply_redis_patch):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def access_token(client):
    hashed_pw = bcrypt.hash("!!Test1234")  # 서비스에서 쓰는 방식 확인 필수!
    user = await BaseUser.create(
        email="test@test.com",
        password=hashed_pw,
        user_type="normal,admin",
        signinMethod="email",
        status="active",
        email_verified=True,
        gender="male",
    )
    seeker = await SeekerUser.create(
        user=user,
        name="테스트유저",
        phone_number="01012345678",
        birth="1990-01-01",
        interests="프론트엔드",
        purposes="취업",
        sources="지인 추천",
    )
    user2 = await BaseUser.create(
        email="test2@test.com",
        password=hashed_pw,
        user_type="business",
        signinMethod="email",
        status="active",
        email_verified=True,
        gender="male",
    )
    corp_user = await CorporateUser.create(
        user=user2,
        company_name="테스트 주식회사",
        business_start_date="2010-01-01",
        business_number="123-45-67890",
        company_description="테스트 기업 설명입니다.",
        manager_name="홍길동",
        manager_phone_number="01012345678",
        manager_email="manager@test.com",
    )

    free_board = await FreeBoard.create(
        user=user,
        title="테스트 자유 개시물",
        content="테스트 내용",
    )

    login_data = {"email": "test@test.com", "password": "!!Test1234"}
    response = await client.post("/api/user/login/", json=login_data)
    access_token = [response.json()["access_token"]]

    login_data = {"email": "test2@test.com", "password": "!!Test1234"}
    response = await client.post("/api/user/login/", json=login_data)
    access_token.append(response.json()["access_token"])

    return access_token


@pytest.mark.asyncio
async def test_create_comment(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    data = {"content": "테스트 댓글"}
    response = await client.post(
        "/api/free-board/1/comment/", json=data, headers=headers
    )

    assert response.status_code == 201
    assert response.json()["content"] == "테스트 댓글"

    await client.post("/api/free-board/1/comment/", json=data, headers=headers)
    await client.post("/api/free-board/1/comment/", json=data, headers=headers)


@pytest.mark.asyncio
async def test_get_comments(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get("/api/free-board/1/comment/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_patch_comment(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    data = {"content": "수정된 댓글"}
    comment_id = 1
    response = await client.patch(
        f"/api/free-board/1/comment/{comment_id}/", json=data, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["content"] == "수정된 댓글"

    headers = {"Authorization": f"Bearer {access_token[1]}"}

    response = await client.patch(
        f"/api/free-board/1/comment/{comment_id}/", json=data, headers=headers
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    comment_id = 1
    response = await client.delete(
        f"/api/free-board/1/comment/{comment_id}/", headers=headers
    )
    assert response.status_code == 200
    assert len(await Comment.all()) == 2
    headers = {"Authorization": f"Bearer {access_token[1]}"}
    comment_id += 1
    response = await client.delete(
        f"/api/free-board/1/comment/{comment_id}/", headers=headers
    )
    assert response.status_code == 403
