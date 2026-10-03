from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from backend.CacheConn import SCRIPT, RedisCache


class RedisCacheTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.cache = RedisCache()
        self.redis_client = MagicMock()
        self.redis_client.get = AsyncMock()
        self.redis_client.delete = AsyncMock()
        self.redis_client.set = AsyncMock()

    async def test_get_returns_cached_value(self):
        self.redis_client.get.return_value = "https://example.com"

        result = await self.cache.get("abc123", self.redis_client)

        self.redis_client.get.assert_awaited_once_with("abc123")
        self.assertEqual(result, "https://example.com")

    async def test_delete_removes_cache_key(self):
        await self.cache.delete("abc123", self.redis_client)

        self.redis_client.delete.assert_awaited_once_with("abc123")

    async def test_set_string_sets_value_with_expiration(self):
        await self.cache.set_string("abc123", 600, "cached-value", self.redis_client)

        self.redis_client.set.assert_awaited_once_with(
            "abc123",
            "cached-value",
            ex=600,
        )

    async def test_update_string_replaces_value_with_expiration(self):
        await self.cache.update_string("abc123", 300, "updated-value", self.redis_client)

        self.redis_client.set.assert_awaited_once_with(
            "abc123",
            "updated-value",
            ex=300,
        )

    async def test_is_allowed_returns_true_when_script_allows_request(self):
        script = AsyncMock(return_value=[1, 60000])
        self.redis_client.register_script.return_value = script

        result = await self.cache.is_allowed(self.redis_client, "ip:127.0.0.1", 10, 60)

        self.redis_client.register_script.assert_called_once_with(SCRIPT)
        script.assert_awaited_once_with(
            keys=["ip:127.0.0.1"],
            args=[10, 60],
            client=self.redis_client,
        )
        self.assertEqual(result, {"allowed": True})

    async def test_is_allowed_returns_false_when_script_denies_request(self):
        script = AsyncMock(return_value=[0, 42000])
        self.redis_client.register_script.return_value = script

        result = await self.cache.is_allowed(self.redis_client, "ip:127.0.0.1", 10, 60)

        self.assertEqual(result, {"allowed": False})