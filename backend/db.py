from typing import Any, Optional
from datetime import datetime

# J:  make queries more generic and reusable, but for now this is can be ok for a mini app.
class PostgresCRUD:

    async def create(self, data, pool):
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO urls (short_code, long_url) VALUES ($1, $2) RETURNING *""",
                data["short_code"],
                data["long_url"],
            )
from typing import Any, Mapping, Optional
import asyncpg


class PostgresCRUD:

    async def create(
        self,
        data: Mapping[str, Any],
        pool: asyncpg.Pool
    ) -> dict:

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO urls (short_code, long_url)
                VALUES ($1, $2)
                RETURNING *
                """,
                data["short_code"],
                data["long_url"],
            )

            return {
                "short_code": row["short_code"],
                "long_url": row["long_url"],
            }

    async def get(self, table: str, value: Any, column: str, pool):
    async def get(
        self,
        table: str,
        value: Any,
        column: str,
        pool: asyncpg.Pool
    ) -> Optional[dict]:

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT * FROM {table} WHERE {column} = $1",
                value,
            )
            if row is None:
                return None

            if row is None:
                return None

            return {
                "id": row["id"],
                "user_id": row["user_id"],
                "short_code": row["short_code"],
                "long_url": row["long_url"],
            }

    async def get_click_count(self, short_code: str, pool) -> int:
    async def get_click_count(
        self,
        short_code: str,
        pool: asyncpg.Pool
    ) -> int:

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT COUNT(clicks.url_id) as click_count FROM clicks INNER JOIN urls ON clicks.url_id = urls.id WHERE urls.short_code = $1",
                short_code,
            )

            if row is None:
                return 0

            return row["click_count"]

    async def insert_click_record(self, data, pool) -> dict:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO clicks (url_id, clicked_at, referrer, country, user_agent)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                data["url_id"],
                data.get("clicked_at"),
                data.get("referrer"),
                data.get("country"),
                data.get("user_agent"),
            )

            return {
                "id": row["id"],
                "url_id": row["url_id"],
                "clicked_at": row["clicked_at"],
                "referrer": row["referrer"],
                "country": row["country"],
                "user_agent": row["user_agent"],
            }

        
    async def delete(self, table: str, value: Any, column: str, pool) -> None:
        async with pool.acquire() as conn:
            await conn.execute(
                f"DELETE FROM {table} WHERE {column} = $1",
                value,
            )

    async def update(self, table: str, value: Any, column: str, data, pool) -> None:
        set_dict = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(data.keys())])
        values = list(data.values())

        async with pool.acquire() as conn:
            await conn.execute(
                f"UPDATE {table} SET {set_dict} WHERE {column} = $1",
                value,
                *values
            )
            return row["click_count"]
