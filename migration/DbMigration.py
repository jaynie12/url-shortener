

# to create a new migration file, run the following command:
# alembic revision --autogenerate -m "your message here"



def create_table_urls():
    return """
   CREATE TABLE urls (
    id  BIGSERIAL PRIMARY KEY,
    user_id  BIGINT REFERENCES users(id),
    short_code  TEXT NOT NULL UNIQUE,
    long_url    TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ
    );
    );
    """

def create_table_users():
    return """
    CREATE TABLE users (
        id BIGSERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

def create_table_clicks():
    return """
    CREATE TABLE clicks (
        id BIGSERIAL PRIMARY KEY,
        url_id BIGINT REFERENCES urls(id),
        clicked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        referrer TEXT,
        country TEXT,
        user_agent TEXT
    );
    """