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
    bounce_rate_percent: float
    device_profile_count: int


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
    average_time_seconds: float | None = None
    minimum_time_seconds: float | None = None
    maximum_time_seconds: float | None = None


class AnalyticsBreakdown(BaseModel):
    name: str
    pageviews: int
    visitors: int
    source: str


class AnalyticsTimeMetrics(BaseModel):
    page_samples: int
    average_page_seconds: float | None
    minimum_page_seconds: float | None
    maximum_page_seconds: float | None
    measured_sessions: int
    average_session_seconds: float | None
    minimum_session_seconds: float | None
    maximum_session_seconds: float | None


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
    devices: list[AnalyticsBreakdown]
    browsers: list[AnalyticsBreakdown]
    operating_systems: list[AnalyticsBreakdown]
    regions: list[AnalyticsBreakdown]
    time_metrics: AnalyticsTimeMetrics
    insights: list[str]
