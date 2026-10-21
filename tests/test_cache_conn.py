from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.cache_conn import SCRIPT, RedisCache


@pytest.fixture
def cache():
    return RedisCache()


@pytest.mark.asyncio
async def test_get_returns_cached_value(cache, redis_client):
    redis_client.get.return_value = "https://example.com"

    result = await cache.get("abc123", redis_client)

    redis_client.get.assert_awaited_once_with("abc123")
    assert result == "https://example.com"


@pytest.mark.asyncio
async def test_delete(cache, redis_client):
    await cache.delete("abc123", redis_client)

    redis_client.delete.assert_awaited_once_with("abc123")


@pytest.mark.parametrize(
    ("method", "ttl", "value"),
    [
        ("set_string", 600, "cached-value"),
        ("update_string", 300, "updated-value"),
    ],
)
@pytest.mark.asyncio
async def test_cache_write_withexpiration(
    cache, redis_client, method, ttl, value
):
    await getattr(cache, method)("abc123", ttl, value, redis_client)

    redis_client.set.assert_awaited_once_with("abc123", value, ex=ttl)


@pytest.mark.parametrize(("script_result", "allowed"), [([1, 60000], True), ([0, 42000], False)])
@pytest.mark.asyncio
async def test_is_allowed_returns_script_result(
    cache, redis_client, script_result, allowed
):
    script = AsyncMock(return_value=script_result)
    redis_client.register_script.return_value = script

    result = await cache.is_allowed(redis_client, "ip:127.0.0.1", 10, 60)

    redis_client.register_script.assert_called_once_with(SCRIPT)
    script.assert_awaited_once_with(
        keys=["ip:127.0.0.1"],
        args=[10, 60],
        client=redis_client,
    )
    assert result == {"allowed": allowed}
