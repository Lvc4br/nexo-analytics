from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.config import settings


class VercelAPIError(Exception):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__("Vercel Analytics request failed")


class VercelAnalyticsClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def _get(self, resource: str, params: dict[str, Any]) -> dict[str, Any]:
        query: dict[str, Any] = {
            "projectId": settings.vercel_project_id,
            **params,
        }
        if settings.vercel_team_id:
            query["teamId"] = settings.vercel_team_id
        elif settings.vercel_team_slug:
            query["slug"] = settings.vercel_team_slug

        try:
            response = await self.client.get(
                f"{settings.vercel_api_base_url.rstrip('/')}/{resource}",
                params=query,
                headers={"Authorization": f"Bearer {settings.vercel_access_token}"},
            )
        except httpx.HTTPError as error:
            raise VercelAPIError(0) from error

        if response.is_error:
            raise VercelAPIError(response.status_code)

        try:
            payload = response.json()
        except ValueError as error:
            raise VercelAPIError(response.status_code) from error
        return payload if isinstance(payload, dict) else {}

    async def aggregate(
        self,
        resource: str,
        *,
        dimensions: list[str],
        since: date,
        until: date,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        payload = await self._get(
            f"{resource}/aggregate",
            {
                "by": dimensions,
                "since": since.isoformat(),
                "until": until.isoformat(),
                "limit": limit,
            },
        )
        data = payload.get("data", [])
        if not isinstance(data, list):
            return []
        return [row for row in data if isinstance(row, dict)]
