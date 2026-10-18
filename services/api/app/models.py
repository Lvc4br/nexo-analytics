from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PortfolioEvent(Base):
    __tablename__ = "portfolio_events"
    __table_args__ = (
        Index("ix_portfolio_events_site_created", "site_id", "created_at"),
        Index("ix_portfolio_events_site_session", "site_id", "session_id"),
        Index("ix_portfolio_events_created", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(100), nullable=False)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_name: Mapped[str] = mapped_column(String(80), nullable=False)
    path: Mapped[str] = mapped_column(String(300), nullable=False)
    device_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    browser_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    os_name: Mapped[str | None] = mapped_column(String(24), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    region_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
