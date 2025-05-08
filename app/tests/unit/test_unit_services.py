import pytest

from app.domain.services.permission import check_author
from app.domain.services.verification import check_existing, check_superuser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.base_exceptions import CustomException


class DummyUser:
    def __init__(self, id, user_type="normal"):
        self.id = id
        self.user_type = user_type


class DummyObject:
    def __init__(self, user_id):
        self.user_id = user_id


@pytest.mark.asyncio
async def test_check_superuser_permission_denied():
    user = DummyUser(id=1, user_type="normal")
    with pytest.raises(PermissionDeniedException):
        check_superuser(user)


@pytest.mark.asyncio
async def test_check_superuser_pass():
    user = DummyUser(id=1, user_type="normal,admin")
    assert check_superuser(user) is None


@pytest.mark.asyncio
async def test_check_existing_not_found():
    class DummyException(CustomException):
        def __init__(self):
            super().__init__(status_code=404, code="not_found", error="Not Found")

    with pytest.raises(DummyException):
        check_existing(None, DummyException)


@pytest.mark.asyncio
async def test_check_existing_found():
    class DummyException(CustomException):
        def __init__(self):
            super().__init__(status_code=404, code="not_found", error="Not Found")

    assert check_existing(object(), DummyException) is None


@pytest.mark.asyncio
async def test_check_author_not_author():
    obj = DummyObject(user_id=1)
    user = DummyUser(id=2)

    with pytest.raises(PermissionDeniedException):
        await check_author(obj, user)


@pytest.mark.asyncio
async def test_check_author_is_author():
    obj = DummyObject(user_id=1)
    user = DummyUser(id=1)

    assert await check_author(obj, user) is None


@pytest.mark.asyncio
async def test_check_author_superuser():
    obj = DummyObject(user_id=1)
    user = DummyUser(id=99, user_type="normal,admin")

    assert await check_author(obj, user) is None
