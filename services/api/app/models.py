from datetime import datetime

from sqlalchemy import DateTime, Index, String
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
