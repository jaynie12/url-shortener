from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Delete, Insert, Select, Update

from backend.db import PostgresCRUD


@pytest.fixture
def crud():
    return PostgresCRUD()


@pytest.mark.asyncio
async def test_create_inserts_url(crud, sqlalchemy_connection, sqlalchemy_engine):
    row = {"short_code": "abc123", "long_url": "https://example.com"}
    result_proxy = MagicMock()
    result_proxy.mappings.return_value.one.return_value = row
    sqlalchemy_connection.execute.return_value = result_proxy

    result = await crud.create(row, sqlalchemy_engine)

    statement = sqlalchemy_connection.execute.await_args.args[0]
    assert isinstance(statement, Insert)
    assert statement.table.name == "urls"
    assert statement.compile().params == row
    sqlalchemy_engine.begin.assert_called_once_with()
    assert result == row


@pytest.mark.asyncio
async def test_get_returns_mapped_row(crud, sqlalchemy_connection, sqlalchemy_engine):
    row = {
        "id": 7,
        "user_id": 4,
        "short_code": "abc123",
        "long_url": "https://example.com",
        "created_at": None,
        "expires_at": None,
    }
    result_proxy = MagicMock()
    result_proxy.mappings.return_value.first.return_value = row
    sqlalchemy_connection.execute.return_value = result_proxy

    result = await crud.get("urls", "abc123", "short_code", sqlalchemy_engine)

    statement = sqlalchemy_connection.execute.await_args.args[0]
    assert isinstance(statement, Select)
    assert statement.compile().params["short_code_1"] == "abc123"
    sqlalchemy_engine.connect.assert_called_once_with()
    assert result == {
        "id": 7,
        "user_id": 4,
        "short_code": "abc123",
        "long_url": "https://example.com",
    }


@pytest.mark.asyncio
async def test_get_returns_none_when_row_is_missing(
    crud, sqlalchemy_connection, sqlalchemy_engine
):
    result_proxy = MagicMock()
    result_proxy.mappings.return_value.first.return_value = None
    sqlalchemy_connection.execute.return_value = result_proxy

    result = await crud.get("urls", "missing", "short_code", sqlalchemy_engine)

    assert result is None


@pytest.mark.parametrize(("count", "expected"), [(3, 3), (0, 0), (None, 0)])
@pytest.mark.asyncio
async def test_get_click_count(
    crud, sqlalchemy_connection, sqlalchemy_engine, count, expected
):
    result_proxy = MagicMock()
    result_proxy.scalar_one_or_none.return_value = count
    sqlalchemy_connection.execute.return_value = result_proxy

    result = await crud.get_click_count("abc123", sqlalchemy_engine)

    statement = sqlalchemy_connection.execute.await_args.args[0]
    assert isinstance(statement, Select)
    assert "count(clicks.url_id)" in str(statement.compile())
    assert "clicks.url_id = urls.id" in str(statement.compile())
    assert "abc123" in statement.compile().params.values()
    assert result == expected


@pytest.mark.asyncio
async def test_insert_click_record(crud, sqlalchemy_connection, sqlalchemy_engine):
    clicked_at = datetime(2025, 1, 2, 3, 4)
    data = {
        "url_id": 7,
        "clicked_at": clicked_at,
        "referrer": "https://referrer.example",
        "country": "CA",
        "user_agent": "test-agent",
    }
    result_proxy = MagicMock()
    result_proxy.mappings.return_value.one.return_value = {"id": 12, **data}
    sqlalchemy_connection.execute.return_value = result_proxy

    result = await crud.insert_click_record(data, sqlalchemy_engine)

    statement = sqlalchemy_connection.execute.await_args.args[0]
    assert isinstance(statement, Insert)
    assert statement.table.name == "clicks"
    assert statement.compile().params == data
    assert "RETURNING clicks.id" in str(
        statement.compile(dialect=postgresql.dialect())
    )
    sqlalchemy_engine.begin.assert_called_once_with()
    assert result == {"id": 12, **data}


@pytest.mark.asyncio
async def test_delete(crud, sqlalchemy_connection, sqlalchemy_engine):
    await crud.delete("urls", "abc123", "short_code", sqlalchemy_engine)

    statement = sqlalchemy_connection.execute.await_args.args[0]
    assert isinstance(statement, Delete)
    assert statement.table.name == "urls"
    assert "short_code" in str(statement.compile())
    assert "abc123" in statement.compile().params.values()


@pytest.mark.asyncio
async def test_update(crud, sqlalchemy_connection, sqlalchemy_engine):
    update_data = MagicMock()
    update_data.model_dump.return_value = {"long_url": "https://new.example"}

    await crud.update(
        "urls", "abc123", "short_code", update_data, sqlalchemy_engine
    )

    update_data.model_dump.assert_called_once_with(exclude_unset=True)
    statement = sqlalchemy_connection.execute.await_args.args[0]
    assert isinstance(statement, Update)
    assert statement.table.name == "urls"
    assert "long_url" in str(statement.compile())
    assert "short_code" in str(statement.compile())
    assert set(statement.compile().params.values()) == {
        "abc123",
        "https://new.example",
    }
