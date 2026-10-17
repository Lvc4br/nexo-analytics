from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.routers.analytics import _date_from_row, _event_rows, _number, _percent_change
from app.routers.auth import require_user


class AnalyticsHelpersTests(TestCase):
    def test_number_ignores_booleans_and_clamps_negative_values(self):
        self.assertEqual(_number({"count": True, "visits": 7}, "count", "visits"), 7)
        self.assertEqual(_number({"visits": -3}, "visits"), 0)

    def test_percent_change_handles_empty_previous_period(self):
        self.assertEqual(_percent_change(10, 5), 100.0)
        self.assertEqual(_percent_change(0, 0), 0.0)
        self.assertIsNone(_percent_change(1, 0))

    def test_date_parser_accepts_vercel_iso_timestamp(self):
        self.assertEqual(_date_from_row({"timestamp": "2026-10-17T00:00:00Z"}).isoformat(), "2026-10-17")
        self.assertIsNone(_date_from_row({"timestamp": "not-a-date"}))

    def test_event_rows_discards_invalid_names_and_orders_by_count(self):
        rows = _event_rows(
            [
                {"eventName": "contact_click", "events": 2, "visitors": 1},
                {"name": "resume_download", "count": 5},
                {"eventName": "  ", "events": 9},
            ]
        )
        self.assertEqual([event.name for event in rows], ["resume_download", "contact_click"])


class ApiRouteTests(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_analytics_requires_authentication(self):
        response = self.client.get("/api/v1/analytics/overview?days=7")
        self.assertEqual(response.status_code, 401)

    def test_login_issues_a_bearer_token_for_valid_credentials(self):
        with (
            patch("app.routers.auth.settings.dashboard_email", "admin@example.com"),
            patch("app.routers.auth.settings.dashboard_password_hash", "password-hash"),
            patch("app.routers.auth.password_hasher.verify", return_value=True),
            patch("app.routers.auth.create_access_token", return_value="test-token"),
        ):
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": "ADMIN@example.com", "password": "a-secure-password"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "test-token")
        self.assertEqual(response.json()["token_type"], "bearer")

    def test_overview_aggregates_mocked_vercel_data(self):
        today = datetime.now(timezone.utc).date()
        previous_end = today - timedelta(days=7)

        async def fake_aggregate(resource, *, dimensions, since, until, limit):
            if dimensions == ["day"] and until == today:
                return [{"timestamp": today.isoformat(), "pageviews": 10, "visitors": 4}]
            if dimensions == ["day"]:
                return [{"timestamp": previous_end.isoformat(), "pageviews": 5, "visitors": 2}]
            if dimensions == ["requestPath"]:
                return [{"requestPath": "/", "pageviews": 10, "visitors": 4}]
            if dimensions == ["eventName"] and until == today:
                return [{"eventName": "contact_click", "events": 3, "visitors": 2}]
            return []

        with (
            patch("app.routers.analytics.settings.vercel_access_token", "test-token"),
            patch("app.routers.analytics.settings.vercel_project_id", "prj_test"),
            patch("app.routers.analytics.settings.vercel_project_domain", "portfolio.example"),
            patch("app.routers.analytics.VercelAnalyticsClient.aggregate", new=AsyncMock(side_effect=fake_aggregate)),
            patch.dict(app.dependency_overrides, {require_user: lambda: "admin@example.com"}),
        ):
            response = self.client.get("/api/v1/analytics/overview?days=7")

        self.assertEqual(response.status_code, 200, response.text)
        overview = response.json()
        self.assertEqual(overview["metrics"]["pageviews"], 10)
        self.assertEqual(overview["metrics"]["visitors"], 4)
        self.assertEqual(overview["metrics"]["events"], 3)
        self.assertEqual(overview["comparison"]["pageviews_percent"], 100.0)
        self.assertEqual(overview["popular_pages"][0]["path"], "/")
        self.assertEqual(overview["events"][0]["name"], "contact_click")
