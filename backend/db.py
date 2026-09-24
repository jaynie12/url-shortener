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

            return {
                "id": row["id"],
                "user_id": row["user_id"],
                "short_code": row["short_code"],
                "long_url": row["long_url"],
            }

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