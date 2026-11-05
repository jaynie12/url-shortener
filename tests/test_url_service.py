from unittest.mock import AsyncMock, MagicMock

import asyncpg
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from UrlService import UrlService


@pytest.fixture
def service():
    service = UrlService.__new__(UrlService)
    service.db = MagicMock()
    service.db.get = AsyncMock()
    service.db.create = AsyncMock()
    service.rate_limit_check = AsyncMock(return_value=True)
    return service


@pytest.fixture
def fake_request():
    fake_request = MagicMock()
    fake_request.app.state.pool = MagicMock()
    return fake_request


@pytest.mark.asyncio
async def test_existing_short_code_returns_conflict(service, fake_request):
    service.db.get.return_value = {"short_code": "abc123"}

    with pytest.raises(HTTPException) as raised:
        await service.create_url("abc123", "https://example.com", fake_request)

    assert raised.value.status_code == 409
    service.db.create.assert_not_awaited()


@pytest.mark.parametrize(
    ("constraint_name", "status_code"),
    [
        ("uq_urls_short_code", 409),
        ("urls_short_code_key", 409),
        ("some_other_constraint", None),
    ],
)
@pytest.mark.asyncio
async def test_unique_violation_handling(
    service, fake_request, constraint_name, status_code
):
    service.db.get.return_value = None
    original_error = asyncpg.UniqueViolationError("duplicate value")
    original_error.constraint_name = constraint_name
    error = IntegrityError("INSERT INTO urls", {}, original_error)
    service.db.create.side_effect = error

    if status_code is None:
        with pytest.raises(IntegrityError) as raised:
            await service.create_url(
                "abc123", "https://example.com", fake_request
            )
        assert raised.value is error
    else:
        with pytest.raises(HTTPException) as raised:
            await service.create_url(
                "abc123", "https://example.com", fake_request
            )
        assert raised.value.status_code == status_code


@pytest.mark.asyncio
async def test_get_url_records_click_on_cache_miss(service, fake_request):
    url_data = {
        "id": 7,
        "user_id": 4,
        "short_code": "abc123",
        "long_url": "https://example.com",
    }
    service.db.get.return_value = url_data
    service.db.insert_click_record = AsyncMock(return_value={"id": 12})
    service.cache = MagicMock()
    service.cache.get = AsyncMock(return_value=None)
    service.cache.set_string = AsyncMock()
    fake_request.app.state.redis_client = MagicMock()

    response = await service.get_url("abc123", fake_request)

    assert response.status_code == 302
    assert response.headers["location"] == url_data["long_url"]
    service.db.insert_click_record.assert_awaited_once()
