from datetime import datetime,timezone

from sqlalchemy import Integer, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column


from app.db import Base

class URL(Base):
    __tablename__ = "urls"

    #used Mapped + mapped_columns(from SQLAlchemy 2.0 Documentation) instead of Column(from old SQLAlchemy 1.x.) to avoid the issue of type annotations being ignored by SQLAlchemy
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_id: Mapped[str] = mapped_column(String, unique=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default= lambda:datetime.now(tz=timezone.utc)
        #used lambda function to avoid the issue of default value being evaluated only once at class definition time
    )

    #added index on short_id to improve query performance when looking up URLs by their short code
    __table_args__ = (
        Index("ix_urls_short_id", "short_id"),
    )

