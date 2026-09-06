from typing import Any, Mapping, Optional
import connections
class PostgresCRUD:

    def __init__(
        self,
    ):
        self.pool = connections.pg_connection()

    def create(self, data: Mapping[str, Any]) -> dict:

        columns = list(data.keys())
        values = list(data.values())

        column_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(values))

        query = f"""
            INSERT INTO {self.table} ({column_sql})
            VALUES ({placeholders})
            RETURNING *
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                row = cursor.fetchone()
                columns = [desc.name for desc in cursor.description]

            conn.commit()

        return dict(zip(columns, row))

    def get(self,table, id: Any, key: str):
        query = f"""
            SELECT *
            FROM {table}
            WHERE {key}=%s
        """
        
        with self.pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (id,)) # JS Sep 24 tuple with one item, not literally id
                return cursor.fetchone()

        return None


    def get_all(
        self,
        *,
        where: Optional[Mapping[str, Any]] = None,
        order_by: Optional[str] = None,
        descending: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[dict]:

        query = f"SELECT * FROM {self.table}"
        params = []

        if where:
            conditions = []

            for column, value in where.items():
                conditions.append(f"{column} = %s")
                params.append(value)

            query += " WHERE " + " AND ".join(conditions)

        if order_by:
            direction = "DESC" if descending else "ASC"
            query += f" ORDER BY {order_by} {direction}"

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)

                rows = cursor.fetchall()
                columns = [desc.name for desc in cursor.description]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    def update(
        self,
        id: Any,
        data: Mapping[str, Any],
    ) -> Optional[dict]:
        """
        Update a row by primary key and return the updated row.
        """
        if not data:
            raise ValueError("data cannot be empty")

        assignments = []
        values = []

        for column, value in data.items():
            assignments.append(f"{column} = %s")
            values.append(value)

        values.append(id)

        query = f"""
            UPDATE {self.table}
            SET {", ".join(assignments)}
            WHERE {self.primary_key} = %s
            RETURNING *
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                row = cursor.fetchone()

                if row is None:
                    conn.rollback()
                    return None

                columns = [desc.name for desc in cursor.description]

            conn.commit()

        return dict(zip(columns, row))

    def delete(self, id: Any) -> bool:
        """
        Delete a row by primary key.

        Returns True if a row was deleted, otherwise False.
        """
        query = f"""
            DELETE FROM {self.table}
            WHERE {self.primary_key} = %s
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (id,))
                deleted = cursor.rowcount > 0

            conn.commit()

        return deleted

    def count(
        self,
        *,
        where: Optional[Mapping[str, Any]] = None,
    ) -> int:
     
        query = f"SELECT COUNT(*) FROM {self.table}"
        params = []

        if where:
            conditions = []
            for column, value in where.items():
                conditions.append(f"{column} = %s")
                params.append(value)

            query += " WHERE " + " AND ".join(conditions)

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()[0]

    def exists(self, id: Any) -> bool:
        query = f"""
            SELECT EXISTS(
                SELECT 1
                FROM {self.table}
                WHERE {self.primary_key} = %s
            )
        """
        
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (id,))
                return cursor.fetchone()[0]
