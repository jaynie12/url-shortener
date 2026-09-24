import sys
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

# Make the project root importable when pytest is launched from another folder.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from url_shortener.backend.main import app  # type: ignore[import-not-found]

client = TestClient(app)


def test_create_url():
	"""The create endpoint returns the generated short URL."""
	with patch("url_shortener.url_endpoints.create_short_url") as create:
		create.return_value = {
			"short_code": "abc123",
			"url": "https://example.com",
		}

		response = client.post("/urls", json={"url": "https://example.com"})

	assert response.status_code == 200
	assert response.json() == {
		"short_code": "abc123",
		"url": "https://example.com",
	}
	create.assert_called_once()


def test_get_url():
	"""The lookup endpoint returns the URL for a short code."""
	with patch("url_shortener.url_endpoints.get_url") as get:
		get.return_value = {
			"short_code": "abc123",
			"url": "https://example.com",
		}

		response = client.get("/urls/abc123")

	assert response.status_code == 200
	assert response.json() == {
		"short_code": "abc123",
		"url": "https://example.com",
	}
	get.assert_called_once_with("abc123")


def test_delete_url():
	"""The delete endpoint confirms that a short URL was removed."""
	with patch("url_shortener.url_endpoints.delete_url") as delete:
		delete.return_value = {"message": "URL deleted"}

		response = client.delete("/urls/abc123")

	assert response.status_code == 200
	assert response.json() == {"message": "URL deleted"}
	delete.assert_called_once_with("abc123")
