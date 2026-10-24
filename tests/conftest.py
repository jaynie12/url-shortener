import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

BACKEND_PATH = str(Path(__file__).resolve().parents[1] / "backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)


@pytest.fixture
def sqlalchemy_connection():
    connection = MagicMock()
    connection.execute = AsyncMock()
    return connection


@pytest.fixture
def sqlalchemy_engine(sqlalchemy_connection):
    engine = MagicMock()
    for method in ("begin", "connect"):
        context_manager = MagicMock()
        context_manager.__aenter__ = AsyncMock(return_value=sqlalchemy_connection)
        context_manager.__aexit__ = AsyncMock(return_value=False)
        getattr(engine, method).return_value = context_manager
    return engine


@pytest.fixture
def redis_client():
    client = MagicMock()
    client.get = AsyncMock()
    client.delete = AsyncMock()
    client.set = AsyncMock()
    return client
