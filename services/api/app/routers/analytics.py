from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import settings
from app.integrations.vercel import VercelAPIError, VercelAnalyticsClient
from app.routers.auth import require_user
from app.schemas.analytics import (
    AnalyticsComparison,
    AnalyticsEvent,
    AnalyticsMetrics,
    AnalyticsOverview,
    PopularPage,
    TrafficDay,
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


def _number(row: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = row.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return max(0, int(value))
    return 0


def _period_total(rows: list[dict[str, Any]], *keys: str) -> int:
    return sum(_number(row, *keys) for row in rows)


def _date_from_row(row: dict[str, Any]) -> date | None:
    raw_value = row.get("timestamp") or row.get("date")
    if not isinstance(raw_value, str):
        return None
    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(raw_value[:10])
        except ValueError:
            return None


def _percent_change(current: int, previous: int) -> float | None:
    if previous == 0:
        return 0.0 if current == 0 else None
    return round(((current - previous) / previous) * 100, 1)


def _pt_number(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def _event_rows(rows: list[dict[str, Any]]) -> list[AnalyticsEvent]:
    events: list[AnalyticsEvent] = []
    for row in rows:
        name = row.get("eventName") or row.get("event_name") or row.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        events.append(
            AnalyticsEvent(
                name=name,
                count=_number(row, "events", "eventCount", "event_count", "count", "pageviews"),
                visitors=_number(row, "visitors", "uniqueVisitors", "unique_visitors"),
            )
        )
    return sorted(events, key=lambda event: event.count, reverse=True)


def _make_insights(
    *,
    pageviews: int,
    visitors: int,
    change: float | None,
    pages: list[PopularPage],
    events: list[AnalyticsEvent],
) -> list[str]:
    insights: list[str] = []
    if change is None:
        insights.append("Ainda não há dados do período anterior para comparar o tráfego.")
    elif change > 0:
        insights.append(f"As visualizações cresceram {_pt_number(change)}% em relação ao período anterior.")
    elif change < 0:
        insights.append(f"As visualizações caíram {_pt_number(abs(change))}% em relação ao período anterior.")
    else:
        insights.append("As visualizações ficaram estáveis em relação ao período anterior.")

    if pages and pageviews:
        top_page = pages[0]
        insights.append(
            f"A página mais acessada foi {top_page.path}, com {_pt_number(top_page.share_percent)}% das visualizações."
        )
    elif visitors == 0:
        insights.append("Nenhuma visita foi registrada neste intervalo; confira se o Web Analytics está ativo no projeto.")

    if events:
        top_event = events[0]
        insights.append(f"O evento mais frequente foi “{top_event.name}”, registrado {top_event.count} vezes.")
    else:
        insights.append("Não há eventos personalizados neste período; confira a instrumentação e o plano da Vercel.")
    return insights


def _translate_vercel_error(error: VercelAPIError) -> HTTPException:
    messages = {
        401: "A credencial da Vercel foi recusada. Confira VERCEL_ACCESS_TOKEN.",
        403: "A credencial não tem acesso ao projeto ou ao Web Analytics.",
        404: "Projeto não encontrado. Confira VERCEL_PROJECT_ID e se o Web Analytics está habilitado.",
        429: "A Vercel limitou as consultas temporariamente. Tente novamente em instantes.",
        0: "Não foi possível conectar à API da Vercel.",
    }
    detail = messages.get(error.status_code, "A API de Web Analytics da Vercel retornou um erro.")
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(
    days: int = Query(default=30, ge=7, le=90),
    _: str = Depends(require_user),
) -> AnalyticsOverview:
    if not settings.vercel_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configure VERCEL_ACCESS_TOKEN e VERCEL_PROJECT_ID no arquivo .env.",
        )

    today = datetime.now(timezone.utc).date()
    period_start = today - timedelta(days=days - 1)
    previous_end = period_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=days - 1)

    timeout = httpx.Timeout(12.0, connect=5.0)

    async def optional_event_aggregate(
        client: VercelAnalyticsClient,
        start: date,
        end: date,
    ) -> list[dict[str, Any]]:
        try:
            return await client.aggregate(
                "events",
                dimensions=["eventName"],
                since=start,
                until=end,
                limit=100,
            )
        except VercelAPIError as error:
            if error.status_code in {402, 403, 404}:
                return []
            raise

    async with httpx.AsyncClient(timeout=timeout) as http_client:
        vercel = VercelAnalyticsClient(http_client)
        try:
            traffic_rows, previous_traffic_rows, page_rows, event_rows, previous_event_rows = await asyncio.gather(
                vercel.aggregate(
                    "visits",
                    dimensions=["day"],
                    since=period_start,
                    until=today,
                    limit=100,
                ),
                vercel.aggregate(
                    "visits",
                    dimensions=["day"],
                    since=previous_start,
                    until=previous_end,
                    limit=100,
                ),
                vercel.aggregate(
                    "visits",
                    dimensions=["requestPath"],
                    since=period_start,
                    until=today,
                    limit=10,
                ),
                optional_event_aggregate(vercel, period_start, today),
                optional_event_aggregate(vercel, previous_start, previous_end),
            )
        except VercelAPIError as error:
            raise _translate_vercel_error(error) from error

    traffic_by_date: dict[date, dict[str, int]] = {}
    for row in traffic_rows:
        row_date = _date_from_row(row)
        if row_date is None or row_date < period_start or row_date > today:
            continue
        traffic_by_date[row_date] = {
            "pageviews": _number(row, "pageviews", "visits", "count"),
            "visitors": _number(row, "visitors", "uniqueVisitors", "unique_visitors"),
        }

    traffic = [
        TrafficDay(date=day, **traffic_by_date.get(day, {"pageviews": 0, "visitors": 0}))
        for day in (period_start + timedelta(days=offset) for offset in range(days))
    ]
    current_pageviews = sum(day.pageviews for day in traffic)
    current_visitors = sum(day.visitors for day in traffic)
    previous_pageviews = _period_total(previous_traffic_rows, "pageviews", "visits", "count")
    previous_visitors = _period_total(previous_traffic_rows, "visitors", "uniqueVisitors", "unique_visitors")

    pages: list[PopularPage] = []
    for row in page_rows:
        path = row.get("requestPath") or row.get("route")
        if not isinstance(path, str):
            continue
        pageviews = _number(row, "pageviews", "visits", "count")
        pages.append(
            PopularPage(
                path=path,
                pageviews=pageviews,
                visitors=_number(row, "visitors", "uniqueVisitors", "unique_visitors"),
                share_percent=round((pageviews / current_pageviews) * 100, 1) if current_pageviews else 0,
            )
        )
    pages.sort(key=lambda page: page.pageviews, reverse=True)

    events = _event_rows(event_rows)
    previous_events = _event_rows(previous_event_rows)
    event_total = sum(event.count for event in events)
    previous_event_total = sum(event.count for event in previous_events)
    pageviews_change = _percent_change(current_pageviews, previous_pageviews)

    return AnalyticsOverview(
        project_id=settings.vercel_project_id,
        domain=settings.vercel_project_domain,
        period_days=days,
        period_start=period_start,
        period_end=today,
        metrics=AnalyticsMetrics(
            pageviews=current_pageviews,
            visitors=current_visitors,
            events=event_total,
            pageviews_per_visitor=round(current_pageviews / current_visitors, 2) if current_visitors else 0,
        ),
        comparison=AnalyticsComparison(
            pageviews_percent=pageviews_change,
            visitors_percent=_percent_change(current_visitors, previous_visitors),
            events_percent=_percent_change(event_total, previous_event_total)
            if event_rows or previous_event_rows else None,
        ),
        traffic=traffic,
        popular_pages=pages,
        events=events,
        insights=_make_insights(
            pageviews=current_pageviews,
            visitors=current_visitors,
            change=pageviews_change,
            pages=pages,
            events=events,
        ),
    )
