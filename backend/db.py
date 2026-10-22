from typing import Any, Mapping

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    Text,
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

metadata = MetaData()
urls = Table(
    "urls", metadata, Column("id", BigInteger), Column("user_id", BigInteger),
    Column("short_code", Text), Column("long_url", Text),
    Column("created_at", DateTime), Column("expires_at", DateTime),
)
clicks = Table(
    "clicks", metadata, Column("id", BigInteger), Column("url_id", BigInteger),
    Column("clicked_at", DateTime), Column("referrer", String),
    Column("country", String), Column("user_agent", String),
)
tables = {"urls": urls, "clicks": clicks}


#getting table nad column names each when we want to use them in t
def table_column(table_name: str, column_name: str):
    table = tables[table_name]
    return table, table.c[column_name]

class PostgresCRUD:
    async def create(self, data: Mapping[str, Any], pool: AsyncEngine) -> dict:
        statement = (
            insert(urls)
            .values(short_code=data["short_code"], long_url=data["long_url"])
            .returning(urls.c.short_code, urls.c.long_url)
        )
        async with pool.begin() as conn:
            result = await conn.execute(statement)
            row = result.mappings().one()
        return {
            "short_code": row["short_code"],
            "long_url": row["long_url"],
        }

    async def get(
        self, table: str, value: Any, column: str, pool: AsyncEngine
    ) -> dict | None:
        selected_table, selected_column = table_column(table, column)
        statement = select(selected_table).where(selected_column == value)
        async with pool.begin() as conn:
            result = await conn.execute(statement)
            row = result.mappings().first()
        if row is None:
            return None
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "short_code": row["short_code"],
            "long_url": row["long_url"],
        }

    async def get_click_count(self, short_code: str, pool: AsyncEngine) -> int:
        statement = (
            select(func.count(clicks.c.url_id))
            .select_from(clicks.join(urls, clicks.c.url_id == urls.c.id))
            .where(urls.c.short_code == short_code)
        )
        async with pool.begin() as conn:
            result = await conn.execute(statement)
            click_count = result.scalar_one_or_none()
        return 0 if click_count is None else click_count

    async def insert_click_record(
        self, data: Mapping[str, Any], pool: AsyncEngine
    ) -> dict:
        statement = (
            insert(clicks)
            .values(
                url_id=data["url_id"],
                clicked_at=data.get("clicked_at"),
                referrer=data.get("referrer"),
                country=data.get("country"),
                user_agent=data.get("user_agent"),
            )
            .returning(clicks)
        )
        async with pool.begin() as conn:
            result = await conn.execute(statement)
            row = result.mappings().one_or_none()
            if row is None:
                raise RuntimeError("Failed to insert click record")
        return {
            "id": row["id"],
            "url_id": row["url_id"],
            "clicked_at": row["clicked_at"],
            "referrer": row["referrer"],
            "country": row["country"],
            "user_agent": row["user_agent"],
        }

    async def delete(
        self, table: str, value: Any, column: str, pool: AsyncEngine
    ) -> None:
        selected_table, selected_column = table_column(table, column)
        statement = delete(selected_table).where(selected_column == value)
        async with pool.begin() as conn:
            await conn.execute(statement)

    async def update(
        self, table: str, value: Any, column: str, data: Any, pool: AsyncEngine
    ) -> None:
        selected_table, selected_column = table_column(table, column)
        values = data.model_dump(exclude_unset=True)
        if not values:
            return
        statement = (
            update(selected_table)
            .where(selected_column == value)
            .values(**values)
        )
        async with pool.begin() as conn:
            await conn.execute(statement)
