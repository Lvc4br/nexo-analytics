from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import re
from threading import Lock

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_database_session
from app.models import PortfolioEvent
from app.schemas.collector import CollectorEvent, CollectorResponse


router = APIRouter(tags=["portfolio collection"])
_requests: dict[str, deque[datetime]] = defaultdict(deque)
_requests_lock = Lock()


def _enforce_rate_limit(origin: str) -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=1)
    with _requests_lock:
        for requests in _requests.values():
            while requests and requests[0] < cutoff:
                requests.popleft()
        requests = _requests[origin]
        if len(requests) >= settings.tracker_rate_limit_per_minute:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Limite de coleta excedido.")
        requests.append(now)


def _header_code(value: str | None, limit: int) -> str | None:
    normalized = (value or "").strip().upper()
    if 1 <= len(normalized) <= limit and re.fullmatch(r"[A-Z0-9-]+", normalized):
        return normalized
    return None


def _estimated_region(request: Request) -> tuple[str | None, str | None]:
    """Read coarse location only from explicitly trusted hosting-edge headers."""
    proxy = settings.geolocation_proxy.casefold().strip()
    if proxy == "vercel":
        return (
            _header_code(request.headers.get("x-vercel-ip-country"), 2),
            _header_code(request.headers.get("x-vercel-ip-country-region"), 8),
        )
    if proxy == "cloudflare":
        return _header_code(request.headers.get("cf-ipcountry"), 2), None
    return None, None


@router.post("/collect", response_model=CollectorResponse, status_code=status.HTTP_202_ACCEPTED)
def collect_event(
    payload: CollectorEvent,
    request: Request,
    origin: str | None = Header(default=None),
    session: Session = Depends(get_database_session),
) -> CollectorResponse:
    normalized_origin = (origin or "").strip().rstrip("/").casefold()
    if not normalized_origin or normalized_origin not in settings.portfolio_origins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origem não autorizada para coleta.")
    if payload.site_id != settings.portfolio_site_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site não encontrado.")

    _enforce_rate_limit(normalized_origin)
    existing = session.get(PortfolioEvent, str(payload.event_id))
    if existing is not None:
        return CollectorResponse(duplicate=True)

    country_code, region_code = _estimated_region(request)
    session.add(
        PortfolioEvent(
            id=str(payload.event_id),
            site_id=payload.site_id,
            session_id=str(payload.session_id),
            event_name=payload.event_name,
            path=payload.path,
            device_type=payload.device_type,
            browser_name=payload.browser_name,
            os_name=payload.os_name,
            country_code=country_code,
            region_code=region_code,
            duration_ms=payload.duration_ms,
            created_at=datetime.now(timezone.utc),
        )
    )
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        if session.get(PortfolioEvent, str(payload.event_id)) is not None:
            return CollectorResponse(duplicate=True)
        raise
    return CollectorResponse()
