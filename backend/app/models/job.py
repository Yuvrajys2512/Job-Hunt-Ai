"""
Job and JobSearch models.

JobSearch: one search request ("frontend jobs in Noida, last 3 weeks")
Job: one individual job listing found during a search

Why separate?
A single search produces many jobs. The search is the parent;
jobs are children. This lets you track which search found which job,
and replay or re-rank searches later.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class SearchStatus(str, PyEnum):
    PENDING   = "pending"    # queued, not started
    RUNNING   = "running"    # agent is actively searching
    COMPLETED = "completed"  # all jobs found and ranked
    FAILED    = "failed"     # something went wrong


class JobSource(str, PyEnum):
    LINKEDIN   = "linkedin"
    NAUKRI     = "naukri"
    INDEED     = "indeed"
    INTERNSHALA = "internshala"


class JobSearch(Base):
    """One search session — parent of all found jobs."""
    __tablename__ = "job_searches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # The raw natural language query the user typed
    query: Mapped[str] = mapped_column(Text, nullable=False)

    # Parsed fields extracted from the query by LLM
    parsed_role: Mapped[str | None]     = mapped_column(String(255))
    parsed_location: Mapped[str | None] = mapped_column(String(255))
    parsed_days: Mapped[int | None]     = mapped_column(Integer)        # "last 3 weeks" → 21

    status: Mapped[SearchStatus] = mapped_column(
        SAEnum(SearchStatus), default=SearchStatus.PENDING
    )
    total_found: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="job_searches")  # noqa: F821
    jobs: Mapped[list["Job"]] = relationship(back_populates="search")


class Job(Base):
    """One job listing found during a search."""
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_searches.id"), nullable=False)

    # Source data scraped from the job site
    source: Mapped[JobSource] = mapped_column(SAEnum(JobSource), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))     # site's own job ID
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    salary_range: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)           # JSON array
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)

    # AI-generated fields
    relevance_score: Mapped[float | None] = mapped_column(Float)     # 0.0 to 1.0
    relevance_reason: Mapped[str | None] = mapped_column(Text)       # LLM explanation

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    search: Mapped["JobSearch"] = relationship(back_populates="jobs")
    application: Mapped["Application | None"] = relationship(back_populates="job")  # noqa: F821
