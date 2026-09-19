from typing import Any, Mapping, Optional
from Connections import ConnectionManager as connections

class PostgresCRUD:

    def __init__(
        self,
    ):
        self.pool = connections.pg_connection()

    def create(self, data: Mapping[str, Any]) -> dict:
        with self.pool.cursor() as cursor:
            cursor.execute(
                "INSERT INTO urls (short_code, long_url) VALUES (%s, %s) RETURNING *",
                (data["short_code"], data["long_url"]),
            )
            row = cursor.fetchone()
            self.pool.commit()
            return {
                "short_code": row[0],
                "long_url": row[1],
            }
    def get(self, table: str, value: Any, column: str) -> Optional[dict]:
        with self.pool.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table} WHERE {column} = %s", (value,))
            row = cursor.fetchone()
            if row is None:
                return None
            return {
                "id": row[0],
                "user_id": row[1],
                "short_code": row[2],
                "long_url": row[3],
            }