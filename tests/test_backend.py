import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from UrlService import UrlService


class FakePostgres:
    def __init__(self):
        self.records = {}

    def get(self, table, value, column):
        return self.records.get(value)

    def create(self, data):
        self.records[data["short_code"]] = data


class FakeCache:
    def __init__(self):
        self.store = {}

    def get(self, cache_key):
        value = self.store.get(cache_key)
        return value.encode("utf-8") if value is not None else None

    def set_string(self, cache_key, ttl, value):
        self.store[cache_key] = value


class UrlServiceTests(unittest.TestCase):
    def make_service(self):
        service = object.__new__(UrlService)
        service.pg = FakePostgres()
        service.cache = FakeCache()
        return service

    def test_create_url_persists_new_short_code(self):
        service = self.make_service()

        service.create_url("abc123", "https://example.com")

        self.assertEqual(service.pg.records["abc123"]["long_url"], "https://example.com")

    def test_create_url_rejects_duplicate_short_code(self):
        service = self.make_service()
        service.pg.create({"short_code": "abc123", "long_url": "https://first.example"})

        with self.assertRaises(HTTPException) as context:
            service.create_url("abc123", "https://second.example")

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Short code already in use")

    def test_get_url_uses_cache_when_available(self):
        service = self.make_service()
        service.cache.store["abc123"] = "https://cached.example"

        result = service.get_url("abc123")

        self.assertEqual(result, "https://cached.example")

    def test_get_url_returns_redirect_after_lookup_in_db_and_caches_result(self):
        service = self.make_service()
        service.pg.create({"short_code": "abc123", "long_url": "https://example.com"})

        result = service.get_url("abc123")

        self.assertIsInstance(result, RedirectResponse)
        self.assertEqual(result.status_code, 301)
        self.assertEqual(result.headers.get("location"), "https://example.com")
        self.assertEqual(service.cache.store["abc123"], "https://example.com")

    def test_get_url_raises_404_when_short_code_is_missing(self):
        service = self.make_service()

        with self.assertRaises(HTTPException) as context:
            service.get_url("missing")

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Short code not found")


if __name__ == "__main__":
    unittest.main()
