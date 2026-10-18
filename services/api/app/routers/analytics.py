from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.config import settings
from app import database
from app.integrations.vercel import VercelAPIError, VercelAnalyticsClient
from app.models import PortfolioEvent
from app.routers.auth import require_user
from app.schemas.analytics import (
    AnalyticsComparison,
    AnalyticsEvent,
    AnalyticsMetrics,
    AnalyticsOverview,
    AnalyticsSources,
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


def _event_rows(rows: list[dict[str, Any]], source: str = "vercel") -> list[AnalyticsEvent]:
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
                sessions=_number(row, "sessions"),
                source=source,
            )
        )
    return sorted(events, key=lambda event: event.count, reverse=True)


def _make_insights(
    *,
    pageviews: int,
    previous_pageviews: int,
    visitors: int,
    change: float | None,
    pages: list[PopularPage],
    events: list[AnalyticsEvent],
    pageviews_source: str,
    engagement_percent: float,
    vercel_pageviews: int | None,
    nexo_pageviews: int,
) -> list[str]:
    insights: list[str] = []
    metric_name = "visualizações registradas pelo Nexo" if pageviews_source == "nexo" else "visualizações"
    if pageviews == 0 and previous_pageviews == 0:
        insights.append("Ainda não há pageviews registrados nos períodos selecionados.")
    elif change is None:
        insights.append(f"Ainda não há dados do período anterior para comparar {metric_name}.")
    elif change > 0:
        insights.append(f"As {metric_name} cresceram {_pt_number(change)}% em relação ao período anterior.")
    elif change < 0:
        insights.append(f"As {metric_name} caíram {_pt_number(abs(change))}% em relação ao período anterior.")
    else:
        insights.append(f"As {metric_name} ficaram estáveis em relação ao período anterior.")

    if pages and pageviews:
        top_page = pages[0]
        insights.append(
            f"A página mais acessada foi {top_page.path}, com {_pt_number(top_page.share_percent)}% das visualizações."
        )
    elif visitors == 0:
        insights.append("Nenhuma sessão foi registrada. Confira se o tracker está instalado no portfólio.")

    if events:
        top_event = events[0]
        insights.append(f"A interação mais frequente foi “{top_event.name}”, registrada {top_event.count} vezes.")
    else:
        insights.append("Ainda não há interações próprias; instrumente cliques relevantes com o tracker Nexo.")

    if visitors:
        insights.append(f"{_pt_number(engagement_percent)}% das sessões tiveram ao menos uma interação registrada pelo Nexo.")
    if vercel_pageviews is not None and nexo_pageviews:
        insights.append(
            "Vercel e Nexo são exibidos como fontes separadas; as visualizações não são somadas para evitar duplicidade."
        )
    return insights


async def _load_vercel(
    period_start: date,
    today: date,
    previous_start: date,
    previous_end: date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]] | None:
    if not settings.vercel_configured:
        return None

    timeout = httpx.Timeout(12.0, connect=5.0)

    async def optional_event_aggregate(
        client: VercelAnalyticsClient,
        start: date,
        end: date,
    ) -> list[dict[str, Any]]:
        try:
            return await client.aggregate("events", dimensions=["eventName"], since=start, until=end, limit=100)
        except VercelAPIError:
            return []

    async with httpx.AsyncClient(timeout=timeout) as http_client:
        vercel = VercelAnalyticsClient(http_client)
        try:
            results = await asyncio.gather(
                vercel.aggregate("visits", dimensions=["day"], since=period_start, until=today, limit=100),
                vercel.aggregate("visits", dimensions=["day"], since=previous_start, until=previous_end, limit=100),
                vercel.aggregate("visits", dimensions=["requestPath"], since=period_start, until=today, limit=100),
                optional_event_aggregate(vercel, period_start, today),
                return_exceptions=True,
            )
            if any(isinstance(result, Exception) for result in results[:3]):
                return None
            return tuple(result if isinstance(result, list) else [] for result in results)
        except VercelAPIError:
            # Keep the dashboard useful using the first-party tracker if Vercel is down or misconfigured.
            return None


def _load_nexo_events(start: date, end_exclusive: date) -> list[PortfolioEvent]:
    start_at = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
    end_at = datetime.combine(end_exclusive, datetime.min.time(), tzinfo=timezone.utc)
    with database.SessionLocal() as session:
        return list(session.scalars(
            select(PortfolioEvent).where(
                PortfolioEvent.site_id == settings.portfolio_site_id,
                PortfolioEvent.created_at >= start_at,
                PortfolioEvent.created_at < end_at,
            )
        ))


def _event_date(event: PortfolioEvent) -> date:
    created_at = event.created_at
    if created_at.tzinfo is None:
        return created_at.date()
    return created_at.astimezone(timezone.utc).date()


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(
    days: int = Query(default=30, ge=7, le=90),
    _: str = Depends(require_user),
) -> AnalyticsOverview:
    today = datetime.now(timezone.utc).date()
    period_start = today - timedelta(days=days - 1)
    previous_end = period_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=days - 1)
    vercel_data = await _load_vercel(period_start, today, previous_start, previous_end)
    vercel_connected = vercel_data is not None

    nexo_rows = _load_nexo_events(previous_start, today + timedelta(days=1))
    traffic_by_date: dict[date, dict[str, int]] = defaultdict(lambda: {"pageviews": 0, "visitors": 0})
    page_counts: dict[str, dict[str, Any]] = defaultdict(lambda: {"pageviews": 0, "sessions": set()})
    custom_events: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "sessions": set()})
    nexo_sessions_by_day: dict[date, set[str]] = defaultdict(set)
    current_session_ids: set[str] = set()
    previous_session_ids: set[str] = set()
    engaged_session_ids: set[str] = set()
    nexo_pageviews = 0
    previous_nexo_pageviews = 0

    for row in nexo_rows:
        event_date = _event_date(row)
        if period_start <= event_date <= today:
            current_session_ids.add(row.session_id)
            nexo_sessions_by_day[event_date].add(row.session_id)
            if row.event_name == "page_view":
                nexo_pageviews += 1
                traffic_by_date[event_date]["pageviews"] += 1
                page_counts[row.path]["pageviews"] += 1
                page_counts[row.path]["sessions"].add(row.session_id)
            else:
                custom_events[row.event_name]["count"] += 1
                custom_events[row.event_name]["sessions"].add(row.session_id)
                engaged_session_ids.add(row.session_id)
        elif previous_start <= event_date <= previous_end:
            previous_session_ids.add(row.session_id)
            if row.event_name == "page_view":
                previous_nexo_pageviews += 1
    for event_date, sessions in nexo_sessions_by_day.items():
        traffic_by_date[event_date]["visitors"] = len(sessions)

    traffic_dates = [period_start + timedelta(days=offset) for offset in range(days)]
    if vercel_connected:
        traffic_rows, previous_traffic_rows, page_rows, vercel_event_rows = vercel_data
        vercel_traffic_by_date: dict[date, dict[str, int]] = {}
        for row in traffic_rows:
            row_date = _date_from_row(row)
            if row_date is None or row_date < period_start or row_date > today:
                continue
            vercel_traffic_by_date[row_date] = {
                "pageviews": _number(row, "pageviews", "visits", "count"),
                "visitors": _number(row, "visitors", "uniqueVisitors", "unique_visitors"),
            }
        traffic_by_date = defaultdict(lambda: {"pageviews": 0, "visitors": 0}, vercel_traffic_by_date)
        current_pageviews = sum(row["pageviews"] for row in vercel_traffic_by_date.values())
        current_visitors = sum(row["visitors"] for row in vercel_traffic_by_date.values())
        previous_pageviews = _period_total(previous_traffic_rows, "pageviews", "visits", "count")
        previous_visitors = _period_total(previous_traffic_rows, "visitors", "uniqueVisitors", "unique_visitors")

        pages: list[PopularPage] = []
        for row in page_rows:
            path = row.get("requestPath") or row.get("route")
            if not isinstance(path, str):
                continue
            pageviews = _number(row, "pageviews", "visits", "count")
            pages.append(PopularPage(
                path=path,
                pageviews=pageviews,
                visitors=_number(row, "visitors", "uniqueVisitors", "unique_visitors"),
                share_percent=round((pageviews / current_pageviews) * 100, 1) if current_pageviews else 0,
        ))
        vercel_events = _event_rows(vercel_event_rows)
        vercel_event_status = "connected" if vercel_events or vercel_event_rows else "unavailable"
        pageviews_source = "vercel"
        visitors_source = "vercel"
    else:
        current_pageviews = nexo_pageviews
        current_visitors = len(current_session_ids)
        previous_pageviews = previous_nexo_pageviews
        previous_visitors = len(previous_session_ids)
        pages = [
            PopularPage(
                path=path,
                pageviews=values["pageviews"],
                visitors=len(values["sessions"]),
                share_percent=round((values["pageviews"] / nexo_pageviews) * 100, 1) if nexo_pageviews else 0,
            )
            for path, values in page_counts.items()
        ]
        vercel_events = []
        vercel_event_status = "unconfigured" if not settings.vercel_configured else "unavailable"
        pageviews_source = "nexo"
        visitors_source = "nexo"

    traffic = [TrafficDay(date=day, **traffic_by_date.get(day, {"pageviews": 0, "visitors": 0})) for day in traffic_dates]
    pages.sort(key=lambda page: page.pageviews, reverse=True)
    events = [
        AnalyticsEvent(name=name, count=values["count"], visitors=0, sessions=len(values["sessions"]), source="nexo")
        for name, values in custom_events.items()
    ]
    events.sort(key=lambda event: event.count, reverse=True)
    event_total = sum(event.count for event in events)
    previous_event_total = sum(1 for row in nexo_rows if previous_start <= _event_date(row) <= previous_end and row.event_name != "page_view")
    previous_events_available = any(previous_start <= _event_date(row) <= previous_end and row.event_name != "page_view" for row in nexo_rows)
    pageviews_change = _percent_change(current_pageviews, previous_pageviews)
    engagement_percent = round((len(engaged_session_ids) / len(current_session_ids)) * 100, 1) if current_session_ids else 0.0

    return AnalyticsOverview(
        project_id=settings.vercel_project_id if vercel_connected else settings.portfolio_site_id,
        domain=settings.vercel_project_domain if vercel_connected else settings.portfolio_domain,
        period_days=days,
        period_start=period_start,
        period_end=today,
        sources=AnalyticsSources(
            vercel="connected" if vercel_connected else ("unavailable" if settings.vercel_configured else "unconfigured"),
            nexo="receiving" if current_session_ids else "no_data",
            vercel_events=vercel_event_status,
        ),
        metrics=AnalyticsMetrics(
            pageviews=current_pageviews,
            visitors=current_visitors,
            events=event_total,
            pageviews_per_visitor=round(current_pageviews / current_visitors, 2) if current_visitors else 0,
            pageviews_source=pageviews_source,
            visitors_source=visitors_source,
            nexo_pageviews=nexo_pageviews,
            vercel_pageviews=current_pageviews if vercel_connected else None,
            nexo_sessions=len(current_session_ids),
            engaged_sessions=len(engaged_session_ids),
            engagement_percent=engagement_percent,
        ),
        comparison=AnalyticsComparison(
            pageviews_percent=pageviews_change,
            visitors_percent=_percent_change(current_visitors, previous_visitors),
            events_percent=_percent_change(event_total, previous_event_total) if previous_events_available else None,
        ),
        traffic=traffic,
        popular_pages=pages,
        events=events,
        vercel_events=vercel_events,
        insights=_make_insights(
            pageviews=current_pageviews,
            previous_pageviews=previous_pageviews,
            visitors=current_visitors,
            change=pageviews_change,
            pages=pages,
            events=events,
            pageviews_source=pageviews_source,
            engagement_percent=engagement_percent,
            vercel_pageviews=current_pageviews if vercel_connected else None,
            nexo_pageviews=nexo_pageviews,
        ),
    )
