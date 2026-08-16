import asyncio
import unittest
from tempfile import TemporaryDirectory

import httpx

from app.config import Settings
from app.garmin.catalog import is_supported_endpoint
from app.main import create_app
from app.storage import HealthCache


class TestHealthAssistant(unittest.TestCase):
    @staticmethod
    async def request(app, method: str, path: str, json: dict | None = None):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, json=json)

    def test_healthz(self):
        with TemporaryDirectory() as directory:
            app = create_app(Settings(database_path=f"{directory}/health.db"))
            response = asyncio.run(self.request(app, "GET", "/healthz"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})

    def test_unauthorized_telegram_chat_is_rejected(self):
        with TemporaryDirectory() as directory:
            settings = Settings(
                database_path=f"{directory}/health.db",
                telegram_allowed_chat_id=123,
            )
            app = create_app(settings)
            response = asyncio.run(
                self.request(
                    app,
                    "POST",
                    "/telegram/webhook",
                    json={"message": {"chat": {"id": 999}, "text": "How did I sleep?"}},
                )
            )
            self.assertEqual(response.status_code, 403)

    def test_cache_round_trip(self):
        with TemporaryDirectory() as directory:
            cache = HealthCache(f"{directory}/health.db")
            cache.put_record(
                endpoint="body_composition",
                source_record_id="weight-1",
                payload={"weight_kg": 80.2},
            )
            rows = cache.query_endpoint(endpoint="body_composition")
            self.assertEqual(rows[0]["payload"], {"weight_kg": 80.2})

    def test_endpoint_catalog_is_explicitly_allowlisted(self):
        self.assertTrue(is_supported_endpoint("sleep"))
        self.assertFalse(is_supported_endpoint("arbitrary_sql"))
