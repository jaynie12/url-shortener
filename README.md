# URL Shortener

## Summary

Create short links and redirect visitors to their original URLs.

## Schema

PostgreSQL stores users, URLs, and click records. 
Each short code is unique.

## Caching Strategy

Redis caches URL lookups for 10 minutes to speed up redirects.

## Installation Steps

1. Start PostgreSQL and Redis.
2. Configure the database connection and `PG_PASSWORD`.
3. Install the project with `pip install -e .` and start the API with `uvicorn main:app --reload`.

## Navigation

- `backend/` — API, database, and cache code.
- `alembic/` — database schema.
- `tests/` — automated tests.
