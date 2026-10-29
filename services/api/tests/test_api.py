from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import configure_database, initialize_database
from app.integrations.vercel import VercelAPIError
from app.routers.analytics import _date_from_row, _event_rows, _number, _percent_change
from app.routers.auth import require_user
from app.routers.collector import _requests


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
        configure_database("sqlite:///:memory:")
        initialize_database()
        _requests.clear()
        self.client = TestClient(app)

    def collect(self, event_name="page_view", *, event_id=None, session_id=None, path="/"):
        return self.client.post(
            "/api/v1/collect",
            headers={"Origin": "https://luca-toniolo.vercel.app"},
            json={
                "event_id": str(event_id or uuid4()),
                "site_id": "lvc4br-lv-portfolio",
                "session_id": str(session_id or uuid4()),
                "event_name": event_name,
                "path": path,
            },
        )

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

    def test_collector_accepts_and_deduplicates_portfolio_events(self):
        event_id = uuid4()
        payload = {"event_id": event_id, "session_id": uuid4()}
        first = self.collect(event_id=payload["event_id"], session_id=payload["session_id"], event_name="contact_click")
        duplicate = self.collect(event_id=payload["event_id"], session_id=payload["session_id"], event_name="contact_click")

        self.assertEqual(first.status_code, 202, first.text)
        self.assertFalse(first.json()["duplicate"])
        self.assertEqual(duplicate.status_code, 202, duplicate.text)
        self.assertTrue(duplicate.json()["duplicate"])

    def test_collector_rejects_unknown_origin_and_site(self):
        response = self.client.post(
            "/api/v1/collect",
            headers={"Origin": "https://attacker.example"},
            json={"event_id": str(uuid4()), "site_id": "lvc4br-lv-portfolio", "session_id": str(uuid4()), "event_name": "page_view", "path": "/"},
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            "/api/v1/collect",
            headers={"Origin": "https://luca-toniolo.vercel.app"},
            json={"event_id": str(uuid4()), "site_id": "wrong-site", "session_id": str(uuid4()), "event_name": "page_view", "path": "/"},
        )
        self.assertEqual(response.status_code, 404)

    def test_collector_applies_rate_limit(self):
        with patch("app.routers.collector.settings.tracker_rate_limit_per_minute", 1):
            first = self.collect()
            second = self.collect("contact_click")

        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 429)

    def test_overview_uses_nexo_tracker_when_vercel_is_not_configured(self):
        session_id = uuid4()
        self.assertEqual(self.collect(session_id=session_id).status_code, 202)
        self.assertEqual(self.collect("contact_click", session_id=session_id, path="/contact").status_code, 202)

        with (
            patch("app.routers.analytics.settings.vercel_access_token", ""),
            patch("app.routers.analytics.settings.vercel_project_id", ""),
            patch.dict(app.dependency_overrides, {require_user: lambda: "admin@example.com"}),
        ):
            response = self.client.get("/api/v1/analytics/overview?days=7")

        self.assertEqual(response.status_code, 200, response.text)
        overview = response.json()
        self.assertEqual(overview["sources"]["vercel"], "unconfigured")
        self.assertEqual(overview["sources"]["nexo"], "receiving")
        self.assertEqual(overview["metrics"]["pageviews"], 1)
        self.assertEqual(overview["metrics"]["visitors"], 1)
        self.assertEqual(overview["metrics"]["nexo_sessions"], 1)
        self.assertEqual(overview["metrics"]["events"], 1)
        self.assertEqual(overview["metrics"]["engagement_percent"], 100.0)
        self.assertEqual(overview["events"][0]["name"], "contact_click")
        self.assertEqual(overview["popular_pages"][0]["path"], "/")

    def test_overview_falls_back_to_nexo_when_vercel_is_unavailable(self):
        session_id = uuid4()
        self.assertEqual(self.collect(session_id=session_id, path="/work").status_code, 202)

        with (
            patch("app.routers.analytics.settings.vercel_access_token", "test-token"),
            patch("app.routers.analytics.settings.vercel_project_id", "prj_test"),
            patch("app.routers.analytics.VercelAnalyticsClient.aggregate", new=AsyncMock(side_effect=VercelAPIError(503))),
            patch.dict(app.dependency_overrides, {require_user: lambda: "admin@example.com"}),
        ):
            response = self.client.get("/api/v1/analytics/overview?days=7")

        self.assertEqual(response.status_code, 200, response.text)
        overview = response.json()
        self.assertEqual(overview["sources"]["vercel"], "unavailable")
        self.assertEqual(overview["metrics"]["pageviews_source"], "nexo")
        self.assertEqual(overview["metrics"]["pageviews"], 1)
        self.assertEqual(overview["popular_pages"][0]["path"], "/work")

    def test_overview_aggregates_mocked_vercel_data(self):
        today = datetime.now(timezone.utc).date()
        previous_end = today - timedelta(days=7)
        tracker_session = uuid4()
        self.assertEqual(self.collect(session_id=tracker_session).status_code, 202)
        self.assertEqual(self.collect(session_id=tracker_session).status_code, 202)
        self.assertEqual(self.collect("contact_click", session_id=tracker_session).status_code, 202)

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
        self.assertEqual(overview["metrics"]["events"], 1)
        self.assertEqual(overview["metrics"]["nexo_pageviews"], 2)
        self.assertEqual(overview["metrics"]["vercel_pageviews"], 10)
        self.assertEqual(overview["metrics"]["pageviews_source"], "vercel")
        self.assertEqual(overview["comparison"]["pageviews_percent"], 100.0)
        self.assertEqual(overview["popular_pages"][0]["path"], "/")
        self.assertEqual(overview["events"][0]["name"], "contact_click")
        self.assertEqual(overview["vercel_events"][0]["name"], "contact_click")


    def test_collector_rejects_query_strings_and_invalid_duration_contract(self):
        invalid_path = self.collect(path="/?email=private@example.com")
        self.assertEqual(invalid_path.status_code, 422)

        payload = {
            "event_id": str(uuid4()),
            "site_id": "lvc4br-lv-portfolio",
            "session_id": str(uuid4()),
            "event_name": "page_view",
            "path": "/",
            "duration_ms": 500,
        }
        response = self.client.post(
            "/api/v1/collect",
            headers={"Origin": "https://luca-toniolo.vercel.app"},
            json=payload,
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_bearer_token_cannot_access_current_user(self):
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer definitely-not-a-valid-token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_is_unavailable_without_admin_configuration(self):
        with (
            patch("app.routers.auth.settings.dashboard_email", ""),
            patch("app.routers.auth.settings.dashboard_password_hash", ""),
        ):
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "a-password"},
            )
        self.assertEqual(response.status_code, 503)
