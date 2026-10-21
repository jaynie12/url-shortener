from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from backend.db import PostgresCRUD


class PostgresCRUDTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.crud = PostgresCRUD()
        self.connection = MagicMock()
        self.connection.fetchrow = AsyncMock()
        self.connection.execute = AsyncMock()
        self.pool = MagicMock()
        self.acquire_context = self.pool.acquire.return_value
        self.acquire_context.__aenter__ = AsyncMock(return_value=self.connection)
        self.acquire_context.__aexit__ = AsyncMock(return_value=False)

    async def test_create_acquires_connection_and_returns_url_fields(self):
        self.connection.fetchrow.return_value = {
            "short_code": "abc123",
            "long_url": "https://example.com",
        }

        result = await self.crud.create(
            {"short_code": "abc123", "long_url": "https://example.com"},
            self.pool,
        )

        self.pool.acquire.assert_called_once_with()
        self.connection.fetchrow.assert_awaited_once()
        args = self.connection.fetchrow.await_args.args
        self.assertIn("INSERT INTO urls", args[0])
        self.assertEqual(args[1:], ("abc123", "https://example.com"))
        self.assertEqual(
            result,
            {"short_code": "abc123", "long_url": "https://example.com"},
        )

    async def test_get_returns_mapped_row(self):
        self.connection.fetchrow.return_value = {
            "id": 7,
            "user_id": 4,
            "short_code": "abc123",
            "long_url": "https://example.com",
        }

        result = await self.crud.get("urls", "abc123", "short_code", self.pool)

        args = self.connection.fetchrow.await_args.args
        self.assertEqual(args, ("SELECT * FROM urls WHERE short_code = $1", "abc123"))
        self.assertEqual(
            result,
            {
                "id": 7,
                "user_id": 4,
                "short_code": "abc123",
                "long_url": "https://example.com",
            },
        )

    async def test_get_returns_none_when_row_is_missing(self):
        self.connection.fetchrow.return_value = None

        result = await self.crud.get("urls", "missing", "short_code", self.pool)

        self.assertIsNone(result)
        self.connection.fetchrow.assert_awaited_once()

    async def test_get_click_count_returns_count(self):
        self.connection.fetchrow.return_value = {"click_count": 3}

        result = await self.crud.get_click_count("abc123", self.pool)

        args = self.connection.fetchrow.await_args.args
        self.assertIn("COUNT(clicks.url_id)", args[0])
        self.assertEqual(args[1], "abc123")
        self.assertEqual(result, 3)

    async def test_get_click_count_returns_zero_when_row_is_missing(self):
        self.connection.fetchrow.return_value = None

        result = await self.crud.get_click_count("abc123", self.pool)

        self.assertEqual(result, 0)

    async def test_insert_click_record_returns_mapped_row(self):
        clicked_at = datetime(2025, 1, 2, 3, 4)
        self.connection.fetchrow.return_value = {
            "id": 12,
            "url_id": 7,
            "clicked_at": clicked_at,
            "referrer": "https://referrer.example",
            "country": "CA",
            "user_agent": "test-agent",
        }
        data = {
            "url_id": 7,
            "clicked_at": clicked_at,
            "referrer": "https://referrer.example",
            "country": "CA",
            "user_agent": "test-agent",
        }

        result = await self.crud.insert_click_record(data, self.pool)

        args = self.connection.fetchrow.await_args.args
        self.assertIn("INSERT INTO clicks", args[0])
        self.assertEqual(args[1:], (7, clicked_at, "https://referrer.example", "CA", "test-agent"))
        self.assertEqual(result, {"id": 12, **data})

    async def test_delete_executes_parameterized_query(self):
        await self.crud.delete("urls", "abc123", "short_code", self.pool)

        self.connection.execute.assert_awaited_once_with(
            "DELETE FROM urls WHERE short_code = $1",
            "abc123",
        )

    async def test_update_executes_parameterized_query(self):
        update_data = MagicMock()
        update_data.model_dump.return_value = {"long_url": "https://new.example"}

        await self.crud.update("urls", "abc123", "short_code", update_data, self.pool)

        update_data.model_dump.assert_called_once_with(exclude_unset=True)
        self.connection.execute.assert_awaited_once_with(
            "UPDATE urls SET long_url = $2 WHERE short_code = $1",
            "abc123",
            "https://new.example",
        )