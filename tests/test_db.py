from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.dml import Delete, Insert, Update

from backend.db import PostgresCRUD


class PostgresCRUDTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.crud = PostgresCRUD()
        self.connection = MagicMock()
        self.result = MagicMock()
        self.connection.execute = AsyncMock(return_value=self.result)
        self.pool = MagicMock()
        self.transaction_context = self.pool.begin.return_value
        self.transaction_context.__aenter__ = AsyncMock(
            return_value=self.connection
        )
        self.transaction_context.__aexit__ = AsyncMock(return_value=False)

    async def test_create_returns_url_fields(self):
        self.result.mappings.return_value.one.return_value = {
            "short_code": "abc123",
            "long_url": "https://example.com",
        }

        result = await self.crud.create(
            {"short_code": "abc123", "long_url": "https://example.com"},
            self.pool,
        )

        statement = self.connection.execute.await_args.args[0]
        self.assertIsInstance(statement, Insert)
        self.assertEqual(
            statement.compile().params,
            {"short_code": "abc123", "long_url": "https://example.com"},
        )
        self.assertEqual(
            result,
            {"short_code": "abc123", "long_url": "https://example.com"},
        )

    async def test_returns_mapped_row(self):
        self.result.mappings.return_value.first.return_value = {
            "id": 7,
            "user_id": 4,
            "short_code": "abc123",
            "long_url": "https://example.com",
        }

        result = await self.crud.get("urls", "abc123", "short_code", self.pool)

        statement = self.connection.execute.await_args.args[0]
        self.assertEqual(
            statement.compile().params,
            {"short_code_1": "abc123"},
        )
        self.assertEqual(
            result,
            {
                "id": 7,
                "user_id": 4,
                "short_code": "abc123",
                "long_url": "https://example.com",
            },
        )

    async def test_returns_none_when_row_is_missing(self):
        self.result.mappings.return_value.first.return_value = None

        result = await self.crud.get("urls", "missing", "short_code", self.pool)

        self.assertIsNone(result)

    async def test_click_count(self):
        self.result.scalar_one_or_none.return_value = 3

        result = await self.crud.get_click_count("abc123", self.pool)

        statement = self.connection.execute.await_args.args[0]
        self.assertIn("count(clicks.url_id)", str(statement))
        self.assertEqual(statement.compile().params, {"short_code_1": "abc123"})
        self.assertEqual(result, 3)

    async def test_click_count(self):
        self.result.scalar_one_or_none.return_value = None

        result = await self.crud.get_click_count("abc123", self.pool)

        self.assertEqual(result, 0)

    async def test_insert_click_record(self):
        clicked_at = datetime(2025, 1, 2, 3, 4)
        data = {
            "url_id": 7,
            "clicked_at": clicked_at,
            "referrer": "https://referrer.example",
            "country": "CA",
            "user_agent": "test-agent",
        }
        self.result.mappings.return_value.one_or_none.return_value = {
            "id": 12,
            **data,
        }

        result = await self.crud.insert_click_record(data, self.pool)

        statement = self.connection.execute.await_args.args[0]
        self.assertIsInstance(statement, Insert)
        self.assertEqual(statement.compile().params, data)
        self.assertEqual(result, {"id": 12, **data})

    async def test_delete_executes_sqlalchemy_statement(self):
        await self.crud.delete("urls", "abc123", "short_code", self.pool)

        statement = self.connection.execute.await_args.args[0]
        self.assertIsInstance(statement, Delete)
        self.assertEqual(statement.compile().params, {"short_code_1": "abc123"})

    async def test_update_skips_empty_patch(self):
        update_data = MagicMock()
        update_data.model_dump.return_value = {}

        await self.crud.update(
            "urls", "abc123", "short_code", update_data, self.pool
        )

        self.connection.execute.assert_not_awaited()
