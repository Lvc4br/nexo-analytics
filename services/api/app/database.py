from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import Engine, create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import REPOSITORY_ROOT, settings
from app.models import Base, PortfolioEvent


def _make_engine(database_url: str | None = None) -> Engine:
    url = database_url or settings.database_url
    if not url:
        database_path = REPOSITORY_ROOT / "services" / "api" / ".data" / "nexo.sqlite3"
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{database_path.as_posix()}"
    elif url.startswith("postgres://"):
        url = f"postgresql+psycopg://{url.removeprefix('postgres://')}"
    elif url.startswith("postgresql://"):
        url = f"postgresql+psycopg://{url.removeprefix('postgresql://')}"

    engine_options: dict[str, object] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            engine_options["poolclass"] = StaticPool
    return create_engine(url, **engine_options)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def configure_database(database_url: str) -> None:
    """Replace the engine; intended for tests and one-process local use."""
    global engine, SessionLocal
    engine.dispose()
    engine = _make_engine(database_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_database_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


def purge_expired_events() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.tracker_event_retention_days)
    with SessionLocal.begin() as session:
        result = session.execute(delete(PortfolioEvent).where(PortfolioEvent.created_at < cutoff))
        return result.rowcount or 0
