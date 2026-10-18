from datetime import date

from pydantic import BaseModel


class AnalyticsMetrics(BaseModel):
    pageviews: int
    visitors: int
    events: int
    pageviews_per_visitor: float
    pageviews_source: str
    visitors_source: str
    nexo_pageviews: int
    vercel_pageviews: int | None
    nexo_sessions: int
    engaged_sessions: int
    engagement_percent: float


class AnalyticsComparison(BaseModel):
    pageviews_percent: float | None
    visitors_percent: float | None
    events_percent: float | None


class TrafficDay(BaseModel):
    date: date
    pageviews: int
    visitors: int


class PopularPage(BaseModel):
    path: str
    pageviews: int
    visitors: int
    share_percent: float


class AnalyticsEvent(BaseModel):
    name: str
    count: int
    visitors: int
    sessions: int = 0
    source: str = "vercel"


class AnalyticsSources(BaseModel):
    vercel: str
    nexo: str
    vercel_events: str


class AnalyticsOverview(BaseModel):
    project_id: str
    domain: str
    period_days: int
    period_start: date
    period_end: date
    sources: AnalyticsSources
    metrics: AnalyticsMetrics
    comparison: AnalyticsComparison
    traffic: list[TrafficDay]
    popular_pages: list[PopularPage]
    events: list[AnalyticsEvent]
    vercel_events: list[AnalyticsEvent]
    insights: list[str]
